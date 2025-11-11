cmake_minimum_required(VERSION 3.28)
project(ChirpNode CXX)

set(CMAKE_CXX_STANDARD  20)

find_package(OpenCV 4 REQUIRED)

add_library(fusionsense
    src/DataAcquisition.cpp
    src/RadarBlock.cpp
    src/RangeDoppler.cpp
    src/Visualizer.cpp
    src/JSONTCP.cpp
)

target_include_directories(fusionsense PUBLIC include)

target_link_libraries(fusionsense PUBLIC
    fftw3
    fftw3f
    fmt
    ${OpenCV_LIBS} # I don't understand CMake, but this is the equivalent of the pkg-config call ig
)


add_executable(test_data_acquisition
    test/DataAcquisition/test_data_acquisition.cpp
)

# target_include_directories(test_data_acquisition PRIVATE
#     include
# )

target_link_libraries(test_data_acquisition
    fusionsense
)

add_executable(non_thread
    test/non_thread/test.cpp
)

target_link_libraries(non_thread
    fusionsense
)


include(CTest)
enable_testing()
