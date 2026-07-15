import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class A733GpuToolingTests(unittest.TestCase):
    def test_vendor_downloads_are_version_and_hash_pinned(self) -> None:
        script = (ROOT / "tools/download_a733_gpu_vendor.sh").read_text()

        self.assertIn("img-bxm-dkms_0.1.0-3_all.deb", script)
        self.assertIn("xserver-xorg-img-bxm_1.21.1-2_arm64.deb", script)
        self.assertRegex(script, r"923ed203[0-9a-f]{56}")
        self.assertRegex(script, r"c8e606db[0-9a-f]{56}")

    def test_module_build_is_locked_to_current_a7z_kernel_and_ddk(self) -> None:
        script = (ROOT / "tools/build_a733_gpu_module.sh").read_text()

        self.assertIn("ARCH=arm64", script)
        self.assertIn("24.2@6603887", script)
        self.assertIn("36.56.104.183", script)
        self.assertIn("Module.symvers", script)
        self.assertIn("comm -23", script)

    def test_package_isolated_from_vendor_xorg_payload(self) -> None:
        script = (ROOT / "tools/package_a733_gpu.sh").read_text()

        self.assertIn("/opt/a733-pvr/$ddk", script)
        self.assertIn("libxcb-dri2-0", script)
        self.assertIn('Option "kmsdev" "/dev/dri/card0"', script)
        self.assertIn("KWIN_DRM_DEVICES=/dev/dri/card0", script)
        self.assertIn("/usr/local/lib/a733-pvr/kwin_wayland", script)
        self.assertNotIn('Environment="LD_LIBRARY_PATH=$prefix/lib"', script)
        self.assertIn("Unsafe Xorg payload entered the package", script)
        self.assertNotRegex(script, re.compile(r"cp .*usr/bin/Xorg"))
        self.assertNotRegex(script, re.compile(r"cp .*modesetting_drv"))
        self.assertNotRegex(script, re.compile(r"cp .*libglamoregl"))

    def test_deployment_falls_back_before_package_install(self) -> None:
        script = (ROOT / "tools/deploy_a733_gpu.sh").read_text()

        fallback = script.index("sed -i 's/^default l0$/default l1/'")
        install = script.index('apt-get install -y "$package"')
        activate = script.rindex("sed -i 's/^default l1$/default l0/'")
        self.assertLess(fallback, install)
        self.assertLess(install, activate)


if __name__ == "__main__":
    unittest.main()
