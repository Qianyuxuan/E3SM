#===============================================================================
#
# Common CMakeLists.txt: a framework for building all CIME components and more
#
# This is a port of cime/scripts/Tools/Makefile. As more components are ported to
# CMake, the directory level of this file will rise to the top-level directory.
#
# We will prefer space-separated strings over lists
#
#===============================================================================

# bmpersch
# - Read modern cmake docs, use modern features
# - Use find_package for trilinos and other TPLS

cmake_minimum_required(VERSION 3.9)
cmake_policy(SET CMP0057 NEW)

project(E3SM C CXX Fortran)

# Include function definitions
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/cmake_util.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/build_mpas_model.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/build_model.cmake)

set(BUILDCONF ${CASEROOT}/Buildconf)

# Do any MPAS builds first since they manage their own flags
build_mpas_models()

# Set global cmake settings
set(CMAKE_MODULE_PATH ${CIMEROOT}/src/CMake)
set(CMAKE_VERBOSE_MAKEFILE TRUE)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/..)

# Set global targets
add_custom_target(genf90
  DEPENDS ${CIMEROOT}/src/externals/genf90/genf90.pl)

# Build E3SM components
set(IDX 0)
set(COMP_CLASSES cpl atm lnd ice ocn rof glc wav iac esp)
set(MPAS_COMPS "mpaso" "mpassi" "mali")
foreach(COMP_NAME IN LISTS COMP_NAMES)
  list(GET COMP_CLASSES ${IDX} COMP_CLASS)
  if (NOT COMP_CLASS STREQUAL "cpl" AND NOT COMP_NAME IN_LIST MPAS_COMPS)
    message("Found component ${COMP_CLASS} model '${COMP_NAME}'")
    add_subdirectory(cmake/${COMP_CLASS})
  endif()

  math(EXPR IDX "${IDX} + 1")
endforeach()

add_subdirectory(cmake/cpl)
