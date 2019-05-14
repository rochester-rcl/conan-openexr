from conans import ConanFile, CMake, tools
import os


class OpenEXRConan(ConanFile):
    name = "OpenEXR"
    version = "2.3.0"
    license = "BSD"
    requires = ("zlib/1.2.8@conan/stable")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "namespace_versioning": [True, False]}
    default_options = "shared=True", "namespace_versioning=True"
    generators = "cmake"

    # TODO use master branch on git because the release version is clearly broken
    # - also need to build both OpenEXR and IlmBase in one go because that's broken too

    def source(self):
        # TODO use master branch of git because releases are no good with CMake
        self.run("git clone https://github.com/openexr/openexr.git openexr")
        tools.replace_in_file("{}/openexr/CMakeLists.txt".format(self.source_folder),
                              "project(OpenEXR VERSION ${OPENEXR_VERSION})",
                              """project(OpenEXR VERSION ${OPENEXR_VERSION})
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
set (CMAKE_CXX_STANDARD 11)""")

    def build(self):
        cmake = CMake(self)

        cmake.definitions.update(
            {"OPENEXR_BUILD_ILMBASE": True,
             "OPENEXR_BUILD_OPENEXR": True,
             "OPENEXR_BUILD_SHARED": self.options.shared,
             "OPENEXR_BUILD_STATIC": not self.options.shared,
             "OPENEXR_BUILD_PYTHON_LIBS": False,
             "CMAKE_PREFIX_PATH": self.deps_cpp_info["zlib"].rootpath,
             })

        cmake.configure(source_dir="{}/openexr".format(self.source_folder))
        cmake.build(target="install")

    def package(self):
        self.copy("*.h", dst="include", src="package/include".format(self.version), keep_path=True)

        self.copy("*.lib", dst="lib", src=".", keep_path=False)
        self.copy("*.a", dst="lib", src=".", keep_path=False)
        self.copy("*.so", dst="lib", src=".", keep_path=False)
        self.copy("*.so.*", dst="lib", src=".", keep_path=False)
        self.copy("*.dylib*", dst="lib", src=".", keep_path=False)

        self.copy("*.dll", dst="bin", src="bin", keep_path=False)

    def package_info(self):
        major, minor, patch = self.version.split(".")
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENEXR_DLL")
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ['include', 'include/OpenEXR']
        libs = ["IlmImf", "IlmImfUtil", "Imath", "IexMath", "Half", "Iex",
                "IlmThread"]

        def set_version(lib):
            return "{}-{}_{}".format(lib, major, minor)

        self.cpp_info.libs = list(map(set_version, libs))
