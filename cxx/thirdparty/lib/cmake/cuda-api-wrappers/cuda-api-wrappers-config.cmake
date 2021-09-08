# Get the directory containing this file.
get_filename_component(cuda-api-wrappers_CURRENT_CONFIG_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)

include(CMakeFindDependencyMacro)
set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
find_dependency(Threads)

# Import targets.
include("${cuda-api-wrappers_CURRENT_CONFIG_DIR}/cuda-api-wrappers-targets.cmake")
