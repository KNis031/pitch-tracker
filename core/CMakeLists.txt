add_library(pitch_core src/yin.cpp)
target_include_directories(pitch_core PUBLIC include)

if(BUILD_TESTING)
    include(FetchContent)
    FetchContent_Declare(
        Catch2
        GIT_REPOSITORY https://github.com/catchorg/Catch2.git
        GIT_TAG        v3.7.1
        GIT_SHALLOW    TRUE
    )
    FetchContent_MakeAvailable(Catch2)

    add_executable(core_tests tests/test_yin.cpp)
    # Catch2WithMain supplies main(), so test files only contain TEST_CASEs.
    target_link_libraries(core_tests PRIVATE pitch_core Catch2::Catch2WithMain)

    # Registers each TEST_CASE as its own ctest test.
    list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)
    include(Catch)
    catch_discover_tests(core_tests)
endif()
