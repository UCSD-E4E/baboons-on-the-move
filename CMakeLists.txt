cmake_minimum_required(VERSION 3.8)

project(baboon-tracking LANGUAGES CXX) # Could add CUDA here in the future

# Set module path so that we can add modules to find system dependencies (we add no modules rn)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake" "${CMAKE_MODULE_PATH}")

# Find packages, some of which are packaged in the repo in THIRDPARTY_DEP_DIR
set(THIRDPARTY_DEP_DIR "${CMAKE_SOURCE_DIR}/thirdparty/lib/cmake")
find_package(OpenCV REQUIRED)
find_package(fmt REQUIRED
	PATHS ${THIRDPARTY_DEP_DIR}
)

# Right now we have a very simple project structure with one target that builds one executable
add_executable(${PROJECT_NAME}
	src/main.cpp
	
	src/preprocessing_pipes.cpp
	src/motion_detecting_pipes.cpp
)

# Require C++17
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

# Add include directories for bundled and unbundled thirdparty deps
target_include_directories(${PROJECT_NAME} PRIVATE
	${OpenCV_INCLUDE_DIRS}
)

# If our min CMake version was >= 3.13 we could use target_link_directories here
# Direct CMake to the shared objects of our bundled thirdparty deps
link_directories(${PROJECT_NAME} PRIVATE "${CMAKE_SOURCE_DIR}/thirdparty/lib}")

# Link dependencies to our executable target
target_link_libraries(${PROJECT_NAME} PRIVATE
	${OpenCV_LIBS}
	fmt::fmt
	pthread # Needed on Linux for std::thread
)

# Set up compiler flags for just C++
if (MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE $<$<COMPILE_LANGUAGE:CXX>/W4 /WX>)
else()
    target_compile_options(${PROJECT_NAME} PRIVATE $<$<COMPILE_LANGUAGE:CXX>:-Wall -Wextra -Werror -pedantic>)
endif()

install(TARGETS ${PROJECT_NAME} DESTINATION bin)

include(CPack)
