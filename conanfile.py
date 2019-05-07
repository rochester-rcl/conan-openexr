from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class OpenEXRConan(ConanFile):
    name = "OpenEXR"
    version = "2.3.0"
    license = "BSD"
    requires = ("IlmBase/2.3.0@jromphf/stable"
                , "zlib/1.2.8@conan/stable"
                )
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "namespace_versioning": [True, False]}
    default_options = "shared=False", "namespace_versioning=True"
    default_options = "shared=False", "namespace_versioning=True"

    def configure(self):
        self.options["IlmBase"].namespace_versioning = self.options.namespace_versioning
        self.options["IlmBase"].shared = self.options.shared

    def source(self):
        tools.download("https://github.com/openexr/openexr/releases/download/v{}/openexr-{}.tar.gz".format(self.version,
                                                                                                           self.version),
                       "openexr.tar.gz")
        tools.untargz("openexr.tar.gz")
        os.unlink("openexr.tar.gz")

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        if "fPIC" in self.options.fields:
            env_build.fpic = self.options.fPIC
        config_dir = "{}/openexr-{}".format(self.source_folder, self.version)
        ilmbase_root = "--with-ilmbase-prefix={}".format(self.deps_cpp_info["IlmBase"].rootpath)
        env_build.configure(configure_dir=config_dir, args=[ilmbase_root])
        env_build.install()

    def package(self):
        self.copy("Imf*.h", dst="include/OpenEXR", src="openexr-{}/IlmImf".format(self.version), keep_path=False)
        self.copy("Imf*.h", dst="include/OpenEXR", src="openexr-{}/IlmImfUtil".format(self.version), keep_path=False)
        self.copy("OpenEXRConfig.h", dst="include/OpenEXR", src="config", keep_path=False)

        self.copy("*IlmImf*.lib", dst="lib", src=".", keep_path=False)
        self.copy("*IlmImf*.a", dst="lib", src=".", keep_path=False)
        self.copy("*IlmImf*.so", dst="lib", src=".", keep_path=False)
        self.copy("*IlmImf*.so.*", dst="lib", src=".", keep_path=False)
        self.copy("*IlmImf*.dylib*", dst="lib", src=".", keep_path=False)

        self.copy("*IlmImf*.dll", dst="bin", src="bin", keep_path=False)
        self.copy("exr*", dst="bin", src="bin", keep_path=False)

    def package_info(self):

        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENEXR_DLL")
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ['include', 'include/OpenEXR']
        self.cpp_info.libs = ["IlmImf", "IlmImfUtil"]
