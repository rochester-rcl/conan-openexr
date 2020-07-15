from conans import ConanFile, CMake, tools
import os


class OpenEXRConan(ConanFile):
    name = "OpenEXR"
    version = "2.4.0"
    license = "BSD"
    requires = "zlib/1.2.8@conan/stable"
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/rochester-rcl/conan-openexr"
    options = {"shared": [True, False], "namespace_versioning": [True, False]}
    default_options = "shared=True", "namespace_versioning=True"
    generators = "cmake"

    # TODO use master branch on git because the release version is clearly broken
    # - also need to build both OpenEXR and IlmBase in one go because that's broken too

    def source(self):
        tools.download(
            "https://github.com/AcademySoftwareFoundation/openexr/archive/v{}.tar.gz".format(
                self.version
            ),
            "openexr.tar.gz",
        )
        tools.untargz("openexr.tar.gz")
        os.unlink("openexr.tar.gz")
        # self.run("cd openexr && git checkout release/2.3".format(self.version))
        tools.replace_in_file(
            "{}/openexr-{}/CMakeLists.txt".format(self.source_folder, self.version),
            "project(OpenEXRMetaProject)",
            """project(OpenEXRMetaProject)
               include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
               if (APPLE)
                    conan_basic_setup(KEEP_RPATHS)
               else()
                    conan_basic_setup()
               endif()
               set (CMAKE_CXX_STANDARD 11)""",
        )

    def build(self):
        cmake = CMake(self)

        cmake.definitions.update(
            {
                "OPENEXR_BUILD_ILMBASE": True,
                "OPENEXR_BUILD_OPENEXR": True,
                "OPENEXR_BUILD_SHARED": self.options.shared,
                "OPENEXR_BUILD_STATIC": not self.options.shared,
                "OPENEXR_BUILD_PYTHON_LIBS": False,
                "OPENEXR_NAMESPACE_VERSIONING": False,
                "CMAKE_PREFIX_PATH": self.deps_cpp_info["zlib"].rootpath,
            }
        )

        cmake.configure(
            source_dir="{}/openexr-{}".format(self.source_folder, self.version)
        )
        cmake.build(target="install")

    def package(self):
        self.copy(
            "*.h",
            dst="include",
            src="package/include".format(self.version),
            keep_path=True,
        )

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
        self.cpp_info.includedirs = ["include", "include/OpenEXR"]
        libs = ["IlmImf", "IlmImfUtil", "Imath", "IexMath", "Half", "Iex", "IlmThread"]

        def set_version(lib):
            return "{}-{}_{}".format(lib, major, minor)

        self.cpp_info.libs = list(map(set_version, libs))
