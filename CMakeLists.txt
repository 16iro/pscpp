cmake_minimum_required(VERSION 3.20)
project(pscpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# BOJ/*/main.cpp 자동 스캔 및 타겟 등록
file(GLOB_RECURSE SOURCES "BOJ/*/main.cpp")

foreach(SRC ${SOURCES})
    get_filename_component(PROB_DIR ${SRC} DIRECTORY)
    get_filename_component(PROB_NUM ${PROB_DIR} NAME)
    get_filename_component(PLATFORM_DIR ${PROB_DIR} DIRECTORY)
    get_filename_component(PLATFORM ${PLATFORM_DIR} NAME)

    set(TARGET "${PLATFORM}_${PROB_NUM}")

    add_executable(${TARGET} ${SRC})
    target_compile_options(${TARGET} PRIVATE
        -O2
        -Wall
        -Wextra
        -std=c++17
    )
    # 바이너리를 build/<PLATFORM>/<NUM>/ 에 출력
    set_target_properties(${TARGET} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${PLATFORM}/${PROB_NUM}"
    )
endforeach()
