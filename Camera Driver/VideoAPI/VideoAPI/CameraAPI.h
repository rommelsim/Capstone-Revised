#pragma once
#include <Windows.h>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <conio.h>
#include <unordered_set>
#include <windows.storage.h>
#include <Mferror.h>
#include <winrt\base.h>
#include <winrt\Windows.Foundation.h>
#include <winrt\Windows.Foundation.Collections.h>
#include <winrt\Windows.Media.Capture.h>
#include <winrt\Windows.Media.Core.h>
#include <winrt\Windows.Media.Devices.h>
#include <winrt\Windows.Media.MediaProperties.h>
#include <winrt\Windows.Media.Capture.Frames.h>

#include <winrt\Windows.Devices.Enumeration.h>
#include <winrt\Windows.Graphics.Imaging.h>
#include <winrt\Windows.Storage.h>
#include <winrt\Windows.Storage.Streams.h>
#include <filesystem>
#include <fstream>

using namespace winrt::Windows::Media::Devices;
using namespace winrt;
using namespace Windows::Media::Capture;
using namespace Windows::Media::MediaProperties;
using namespace Windows::Media::Capture::Frames;
using namespace Windows::Foundation;
using namespace Windows::Foundation::Collections;
using namespace Windows::Devices::Enumeration;
using namespace Windows::Storage;
using namespace Windows::Graphics::Imaging;
using namespace Windows::Media::Core;

#include <mutex>  // For thread safety
std::mutex logMutex;  // Ensure thread-safe logging
void LogMessage(const std::wstring& message) {
    std::lock_guard<std::mutex> lock(logMutex);  // Lock to prevent race conditions

    std::wofstream logFile("log.txt", std::ios::app);  // Open log file in append mode
    if (!logFile) {
        std::wcerr << L"Failed to open log file!\n";
        return;
    }

    // Get current time
    time_t now = time(0);
    struct tm timeInfo;
    localtime_s(&timeInfo, &now);  // Safe version of localtime()

    // Format time as [YYYY-MM-DD HH:MM:SS]
    wchar_t timeBuffer[20];
    wcsftime(timeBuffer, sizeof(timeBuffer) / sizeof(wchar_t), L"%Y-%m-%d %H:%M:%S", &timeInfo);

    // Write log entry
    logFile << L"[" << timeBuffer << L"] " << message << std::endl;
    logFile.close();
}

namespace API {
    enum MODE {
        VIDEO = 1,
        PICTURE = 2,
    };

	class CameraHelper {
    private:
        IVectorView<MediaFrameSourceGroup> m_SourceGroups;		// Hold references to sources 
        MediaFrameReader m_PreviewFrameReader;					// Mock Preview
        std::unordered_set<std::wstring> uniqueIds;				// Store unique Ids to prevent duplicates
        MediaFrameFormat optimalFormat = nullptr;

    public:
        CameraHelper() :m_SourceGroups(nullptr), m_PreviewFrameReader(nullptr) {

        }

        void WakeCamera(MediaCapture mediaCapture)
        {
            // start Preview to get the 3A running and wait for convergence.
            MediaFrameSource previewframeSource(nullptr);
            MediaStreamType streamTypelookup = MediaStreamType::VideoPreview;

            // Try to find the suitable pin where 3A will be running.
            // Start by looking for a preview pin , if not found look for record pin 
            // However exit the loop when preview and record pins are not available as just running the photo pin cannot converge 3A
            while ((previewframeSource == nullptr) && (streamTypelookup != MediaStreamType::Photo))
            {
                auto frameSourceIter = mediaCapture.FrameSources().First();
                // If there is no preview pin, find a record pin
                while (frameSourceIter.HasCurrent())
                {
                    auto frameSource = frameSourceIter.Current().Value();
                    if (frameSource.Info().MediaStreamType() == streamTypelookup && frameSource.Info().SourceKind() == MediaFrameSourceKind::Color)
                    {
                        previewframeSource = frameSource;
                        break;
                    }
                    frameSourceIter.MoveNext();
                }
                streamTypelookup = (streamTypelookup == MediaStreamType::VideoPreview) ? MediaStreamType::VideoRecord : MediaStreamType::Photo;
            }

            m_PreviewFrameReader = mediaCapture.CreateFrameReaderAsync(previewframeSource).get();
            m_PreviewFrameReader.AcquisitionMode(MediaFrameReaderAcquisitionMode::Realtime);
            m_PreviewFrameReader.StartAsync().get();
            std::cout << "\nDraining samples for one second from the pipeline to enable 3A convergence\n";
            std::cout << "\Waking Camera...\n";
            Sleep(10000);           // allow the camera to wake and autofocus.
            std::cout << "\Camera On!\n";
        }

        MediaCapture InitCamera() {

            std::cout << "\nImage Capture Tool: V1.0\n";
            MediaCapture mediaCapture;

            auto settings = MediaCaptureInitializationSettings();
            auto filteredGroups = GetSourceGroupList();
            if (filteredGroups.Size() < 1) {
                std::cout << "Error No suitable capture sources found";
                throw_hresult(MF_E_NO_CAPTURE_DEVICES_AVAILABLE);
            }

            // NOTE: Remember to disable all other cameras on your host. You can check Device Manager and disable everything other than Kiyo.
            int cam_idx = 0;
            auto selectedSrc = filteredGroups.GetAt(cam_idx);

            if (selectedSrc == nullptr)
            {
                throw_hresult(MF_E_OUT_OF_RANGE);
            }



            settings.SourceGroup(selectedSrc.SourceGroup());

            // If user explicitly selected a non-photo pin to take the photo
            if (selectedSrc.MediaStreamType() != MediaStreamType::Photo)
            {
                settings.PhotoCaptureSource(PhotoCaptureSource::VideoPreview);
            }
            else
            {
                // We hope that auto will select the best photo pin options
                settings.PhotoCaptureSource(PhotoCaptureSource::Auto);
            }

            settings.StreamingCaptureMode(StreamingCaptureMode::Video);

            // Set format on the mediacapture frame source
            mediaCapture.InitializeAsync(settings).get();

            auto frameSrc = mediaCapture.FrameSources().TryLookup(selectedSrc.Id());
            if (!frameSrc) {
                std::cout << "Error in getting frame source\n";
                throw_hresult(MF_E_NOT_FOUND);
            }

            bool found1080p = false;
            for (const MediaFrameFormat& format : frameSrc.SupportedFormats()) {
                if (format.VideoFormat().Width() == 1920 && format.VideoFormat().Height() == 1080) {
                    optimalFormat = format;
                    found1080p = true;
                    break;
                }
            }

            if (!found1080p) {
                uint32_t maxResolution = 0;
                for (const MediaFrameFormat& format : frameSrc.SupportedFormats()) {
                    auto res = format.VideoFormat().Width() * format.VideoFormat().Height();
                    if (res > maxResolution) {
                        maxResolution = res;
                        optimalFormat = format;
                    }
                }
            }

            if (optimalFormat) {
                frameSrc.SetFormatAsync(optimalFormat).get();
                std::wcout << "Resolution set to: " << optimalFormat.VideoFormat().Width()
                    << " X " << optimalFormat.VideoFormat().Height() << "\n";
            }
            else {
                std::cout << "No optimal resolution found.";
                throw_hresult(MF_E_NOT_FOUND);
            }

            WakeCamera(mediaCapture);
            return mediaCapture;
        }
        
        IVector<MediaFrameSourceInfo> GetSourceGroupList() {
            std::vector<MediaFrameSourceInfo> filteredSourceInfos;
            m_SourceGroups = MediaFrameSourceGroup::FindAllAsync().get();

            auto isConsumableSource = [](const MediaFrameSourceInfo& sourceInfo) {
                return (sourceInfo.MediaStreamType() == MediaStreamType::Photo
                    || sourceInfo.MediaStreamType() == MediaStreamType::VideoPreview
                    || sourceInfo.MediaStreamType() == MediaStreamType::VideoRecord)
                    && sourceInfo.SourceKind() == MediaFrameSourceKind::Color;
                };


            for (const auto& sourceGroup : m_SourceGroups)
            {
                for (const auto& sourceInfo : sourceGroup.SourceInfos())
                {
                    std::wstring srcID = sourceInfo.Id().c_str();

                    if (isConsumableSource(sourceInfo) && uniqueIds.insert(srcID).second)
                    {
                        filteredSourceInfos.push_back(sourceInfo);
                    }
                }
            }

            if (filteredSourceInfos.empty())
            {
                throw_hresult(MF_E_NOT_AVAILABLE);
            }

            return winrt::single_threaded_vector(std::move(filteredSourceInfos));
        }


        void RecordVideo(MediaCapture& mediaCapture, uint32_t durationInSeconds) {
            try {
                // Validate MediaCapture instance
                if (!mediaCapture) {
                    std::wcerr << L"MediaCapture instance is invalid.\n";
                    throw_hresult(E_POINTER);
                }

                // Get the SavedPictures folder
                auto picturesFolder = Windows::Storage::KnownFolders::SavedPictures();

                // Create or open the "videos" folder
                auto videoFolder = picturesFolder.CreateFolderAsync(L"videos", Windows::Storage::CreationCollisionOption::OpenIfExists).get();

                // Create a unique file name for the video
                auto videoFile = videoFolder.CreateFileAsync(L"recording.mp4", Windows::Storage::CreationCollisionOption::GenerateUniqueName).get();
                std::wcout << L"Recording file will be saved as: " << videoFile.Path().c_str() << "\n";

                // Set encoding properties for the video
                auto encodingProperties = MediaEncodingProfile::CreateMp4(VideoEncodingQuality::HD1080p);

                // Start video recording
                std::cout << "Recording started...\n";
                mediaCapture.StartRecordToStorageFileAsync(encodingProperties, videoFile).get();

                // Wait for the specified duration
                std::cout << "Recording in progress...\n";
                std::this_thread::sleep_for(std::chrono::seconds(durationInSeconds));

                // Stop video recording
                mediaCapture.StopRecordAsync().get();
                std::cout << "Recording stopped. Video saved to: ";
                std::wcout << videoFile.Path().c_str() << "\n";
            }
            catch (hresult_error const& ex) {
                std::wcerr << L"Failed to record video: " << ex.message().c_str() << L" (HRESULT: " << std::hex << ex.code() << L")\n";
                throw;
            }
            catch (std::exception const& ex) {
                std::cerr << "Standard exception caught: " << ex.what() << std::endl;
                throw;
            }
        }

        void TakePhotos(MediaCapture& mediaCapture, uint32_t durationInSeconds)
        {
            try
            {
                if (!mediaCapture) {
                    std::wcerr << L"MediaCapture instance failed.";
                    LogMessage(L"MediaCapture instance failed.");
                    throw_hresult(E_POINTER);
                }
                wchar_t buffer[MAX_PATH];
                GetModuleFileName(0, buffer, MAX_PATH);
                std::filesystem::path exePath(buffer);
                auto currentDir = std::filesystem::current_path();
                std::filesystem::path picturesPath = exePath.parent_path() / "pictures";
                LogMessage(L"Picture Path: " + picturesPath.wstring());

                // Create the "pictures" folder if it doesn't exist
                if (!std::filesystem::exists(picturesPath))
                {
                    std::filesystem::create_directory(picturesPath);
                    LogMessage(L"Creating path: " + picturesPath.wstring());
                }
                auto picFileName = currentDir / "photo.jpg";
                auto uniqueFileName = picFileName;
                int count = 1;
                while (std::filesystem::exists(picFileName)) {
                    uniqueFileName = picturesPath / (L"Photo_" + std::to_wstring(count++) + L".jpg");
                }
                std::wcout << L"Photo taken file will be saved as: " << uniqueFileName.wstring() << "\n";
                LogMessage(L"Photo taken file will be saved as: " + uniqueFileName.wstring() + L"\n");

                auto imageProperties = ImageEncodingProperties::CreateJpeg();

                auto storageFolder = winrt::Windows::Storage::StorageFolder::GetFolderFromPathAsync(picturesPath.wstring()).get();
                auto storageFile = storageFolder.CreateFileAsync(uniqueFileName.filename().wstring(), winrt::Windows::Storage::CreationCollisionOption::GenerateUniqueName).get();
                mediaCapture.CapturePhotoToStorageFileAsync(imageProperties, storageFile).get();

                std::wcout << L"Photo saved to: " << uniqueFileName.wstring() << "\n";
                LogMessage(L"Photo saved to: " + uniqueFileName.wstring() + L"\n");

                // Delay before capturing the next photo
                std::this_thread::sleep_for(std::chrono::seconds(durationInSeconds));
            }
            catch (hresult_error const& ex)
            {
                std::wcerr << L"Failed to take photos: "
                    << ex.message().c_str()
                    << L" (HRESULT: 0x"
                    << std::hex << ex.code() << L")\n";
                //LogMessage(L"Failed to take photos: " + ex.message() + L" (HRESULT: 0x" + ex.code() + L")\n");
                LogMessage(L"Failed to take photos: " + std::wstring(ex.message()) + L" (HRESULT: 0x" + std::to_wstring(ex.code().value) + L")");
                throw;
            }
            catch (std::exception const& ex)
            {
                std::cerr << "Standard exception caught: " << ex.what() << std::endl;
                std::string errorMsg = "Standard exception caught: " + std::string(ex.what());
                std::wstring wideErrorMsg(errorMsg.begin(), errorMsg.end());
                LogMessage(wideErrorMsg);
                throw;
            }
        }

	};
}