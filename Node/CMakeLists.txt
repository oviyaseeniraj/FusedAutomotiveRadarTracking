cmake_minimum_required(VERSION 3.28)
project(ChirpNode)


add_library(fusionsense INTERFACE
    src/temp.cpp
)

target_include_directories(fusionsense INTERFACE include)

include(CTest)
enable_testing()
