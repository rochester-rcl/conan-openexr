cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 11)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(testPackage main.cpp drawImage.cpp previewImageExamples.cpp testMatrix.cpp)

include_directories(${CMAKE_CURRENT_SOURCE_DIR} ${CONAN_INCLUDE_DIRS})
TARGET_LINK_LIBRARIES(testPackage ${CONAN_LIBS})
# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
