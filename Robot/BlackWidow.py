from SynapseWebDriver import SynapseWebDriverClass
from robot.api.deco import keyword

isFinished = False

@keyword("Perform Chroma Test BlackWidow V4")
def PerformChromaTestBlackWidowV4():
    global isFinished

    lighting_selector = '#root > div > div.nav-tabs > div.navs-wrapper > div:nth-child(2)'
    tmp = '#body-wrapper > div > div.widget-col.col-right.flex > div > div > div:nth-child(2) > div.modes-area.active > div.flex.chroma-flex-row > div.dropdown-area > div.s3-dropdown > div.selected.raw-text'
    static = '#body-wrapper > div > div.widget-col.col-right.flex > div > div > div:nth-child(2) > div.modes-area.active > div.flex.chroma-flex-row > div.dropdown-area > div.s3-options.unsetZ.flex.expand > div:nth-child(9)'

    driver = SynapseWebDriverClass()
    driver.switchSynapseTabTo("BLACKWIDOW V4 75%")
    driver.clickOnElement(lighting_selector)
    driver.clickOnElement(tmp)
    driver.clickOnElement(static)

    isFinished = True

@keyword("Check Status")
def CheckStatus():
    global isFinished
    return isFinished

# PerformChromaTestBlackWidowV4()