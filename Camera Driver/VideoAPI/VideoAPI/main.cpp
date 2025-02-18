#include <iostream>
#include "CameraAPI.h"

// foo.exe 10 1
int main(int argc, char* argv[]) {

    // Check if the user has provided the number of videos as a command-line argument
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <number_of_videos>" << std::endl;
        return -1;
    }

    // Parse the number of videos from the command-line argument
    int iterations = std::atoi(argv[1]);
    int mode = std::atoi(argv[2]);

    if (iterations <= 0) {
        std::cerr << "Error: The number of videos must be a positive integer." << std::endl;
        return -1;
    }

    // Create an instance of the CameraHelper class
    API::CameraHelper cameraHelper;
        
    try {

        MediaCapture mediaCapture = cameraHelper.InitCamera();
        for (int i = 1; i <= iterations; ++i) {
            uint32_t durationInSeconds = 10;  // Adjust duration as needed
            if (mode == API::MODE::VIDEO)   cameraHelper.RecordVideo(mediaCapture, durationInSeconds);
            else if (mode == API::MODE::PICTURE) cameraHelper.TakePhotos(mediaCapture, 1);
        }
        std::cout << "All data have been taken successfully.\n";
    }
    catch (const std::exception& e) {
        std::cerr << "An error occurred: " << e.what() << std::endl;
    }

    return 0;
}
