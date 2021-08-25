cmake_minimum_required(VERSION 3.12)

project(baboon-tracking LANGUAGES CXX) # Could add CUDA here in the future

option(USE_CUDA "Include CUDA headers and use CUDA-accelerated functions" OFF)
option(STATIC_LINK_OPENCV "Statically link minimal OpenCV dependencies to create a more portable binary" OFF)

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
	
	src/util/thread_pool.cpp

	src/drake/common/drake_assert_and_throw.cpp
	src/drake/math/discrete_algebraic_riccati_equation.cpp
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
if (STATIC_LINK_OPENCV)
	# In the static linking case we manually specify the exact things to statically link with so that we end up with a minimal binary
	set(OpenCV_LIBS opencv_core opencv_calib3d opencv_features2d opencv_imgproc opencv_photo opencv_imgcodecs opencv_videoio)
	if (USE_CUDA)
		list(APPEND OpenCV_LIBS opencv_cudaarithm opencv_cudafeatures2d opencv_cudaimgproc opencv_cudawarping)
	endif()
else()
	target_compile_definitions(${PROJECT_NAME} PRIVATE DEBUG_DRAW=1)
endif()

target_link_libraries(${PROJECT_NAME} PRIVATE
	$<IF:$<CONFIG:STATIC_LINK_OPENCV>,-static,-dynamic>
	${OpenCV_LIBS}
	$<IF:$<CONFIG:STATIC_LINK_OPENCV>,-dynamic,-dynamic>
	fmt::fmt-header-only
	pthread # Needed on Linux for std::thread
)

message(STATUS "OpenCV libs: ${OpenCV_LIBS}")

# Sanitizers
if (SANITIZE)
	target_link_libraries(${PROJECT_NAME} PRIVATE
		-fsanitize=undefined,integer,address
	)
endif()

# Set the HAS_CUDA macro
if (USE_CUDA)
	target_compile_definitions(${PROJECT_NAME} PRIVATE USE_CUDA=1)
endif()

# Set up compiler flags for just C++
if (MSVC)
	target_compile_options(${PROJECT_NAME} PRIVATE $<$<COMPILE_LANGUAGE:CXX>/W4 /WX>)
else()
	target_compile_options(${PROJECT_NAME} PRIVATE $<$<COMPILE_LANGUAGE:CXX>:-Wall -Wextra -Werror -pedantic>)
endif()

install(TARGETS ${PROJECT_NAME} DESTINATION bin)

include(CPack)
