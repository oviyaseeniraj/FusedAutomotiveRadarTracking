cmake_minimum_required(VERSION 3.28)
project(ChirpNode)


add_library(fusionsense
    src/DataAcquisition.cpp
    src/RadarBlock.cpp
    src/RangeDoppler.cpp
    src/Visualizer.cpp
)

target_include_directories(fusionsense PUBLIC include)

include(CTest)
enable_testing()
