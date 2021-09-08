#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cuda-api-wrappers::nvtx" for configuration "Release"
set_property(TARGET cuda-api-wrappers::nvtx APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cuda-api-wrappers::nvtx PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcuda-nvtx-wrappers.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS cuda-api-wrappers::nvtx )
list(APPEND _IMPORT_CHECK_FILES_FOR_cuda-api-wrappers::nvtx "${_IMPORT_PREFIX}/lib/libcuda-nvtx-wrappers.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
