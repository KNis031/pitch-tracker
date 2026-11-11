cmake_minimum_required(VERSION 3.22)
project(pitch_tracker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)  # plain -std=c++20, not GNU dialect
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Defines BUILD_TESTING (ON by default) and enables ctest from the build root.
include(CTest)

add_subdirectory(core)
# add_subdirectory(plugin)  # B3
