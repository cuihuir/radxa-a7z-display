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
        self.assertIn("Version: 24.2.6603887+gpu8", script)
        self.assertIn("5.15.147-21.1+display2", script)
        self.assertIn("5.15.147-21.2", script)
        self.assertIn(
            'exec /usr/local/lib/a733-pvr/kwin_wayland "\\$@"', script
        )
        self.assertIn("kwin_wayland.new <<'ENV'", script)
        self.assertIn('"\\$(readlink /usr/local/bin/kwin_wayland', script)
        self.assertIn("dpkg-divert --package a733-pvr-gpu --add --rename", script)
        self.assertIn("kscreenlocker_greet.a733-pvr-distrib", script)
        self.assertIn('exec /usr/bin/Xwayland "\\$@"', script)
        self.assertIn("/opt/a733-xwayland/24.1.6/Xwayland", script)
        self.assertIn('"\\$@" -glamor es', script)
        self.assertIn("4:5.27.5-3+a7331", script)
        self.assertGreaterEqual(
            script.count(
                "unset LD_LIBRARY_PATH LIBGL_DRIVERS_PATH VK_DRIVER_FILES "
                "OCL_ICD_VENDORS KWIN_DRM_DEVICES"
            ),
            2,
        )
        self.assertNotRegex(
            script, re.compile(r"cat > /etc/(?:environment\.d|profile\.d)")
        )
        self.assertNotIn('Environment="LD_LIBRARY_PATH=$prefix/lib"', script)
        self.assertIn("Unsafe Xorg payload entered the package", script)
        self.assertNotRegex(script, re.compile(r"cp .*usr/bin/Xorg"))
        self.assertNotRegex(script, re.compile(r"cp .*modesetting_drv"))
        self.assertNotRegex(script, re.compile(r"cp .*libglamoregl"))

    def test_xwayland_package_is_pinned_and_scoped(self) -> None:
        script = (ROOT / "tools/package_a733_xwayland.sh").read_text()

        self.assertIn(
            "a58c2908da43d45bdf28f63b692c260452b9f455ce9aa36cd52a33190f389135",
            script,
        )
        self.assertIn("/opt/a733-xwayland/$version", script)
        self.assertIn("a733-pvr-gpu (>= 24.2.6603887+gpu7)", script)
        self.assertIn("kwin-common (>= 4:5.27.5-3+a7331)", script)
        self.assertIn("/usr/local/sbin/a733-pvr-control enable", script)
        self.assertNotIn("/usr/bin/Xwayland", script)

    def test_kwin_builder_uses_the_tracked_render_node_patch(self) -> None:
        script = (ROOT / "tools/build_a733_kwin.sh").read_text()

        self.assertIn("0001-linux-dmabuf-use-egl-render-node.patch", script)
        self.assertIn("4:5.27.5-3+a7331", script)
        self.assertIn("dpkg-buildpackage -b -uc -us", script)
        self.assertIn("cuihuir <cuihuir@163.com>", script)
        self.assertIn("sed 's#  \\./#  #' > SHA256SUMS", script)
        self.assertNotIn('sha256sum "$output"/*.deb', script)

    def test_x11_egl_probe_uses_each_egl_native_visual(self) -> None:
        source = (ROOT / "tools/a733_x11_egl_probe.c").read_text()

        self.assertIn("EGL_NATIVE_VISUAL_ID", source)
        self.assertIn("XGetVisualInfo", source)
        self.assertIn("eglMakeCurrent(display, surface, surface, context)", source)
        self.assertIn("glGetString(GL_RENDERER)", source)
        self.assertIn("eglSwapBuffers(display, surface)", source)

    def test_deployment_falls_back_before_package_install(self) -> None:
        script = (ROOT / "tools/deploy_a733_gpu.sh").read_text()

        self.assertIn('ge 5.15.147-21.1+display2', script)
        self.assertIn('lt 5.15.147-21.2', script)
        fallback = script.index("sed -i 's/^default l0$/default l1/'")
        install = script.index('apt-get install --fix-broken -y "$package"')
        activate = script.rindex("sed -i 's/^default l1$/default l0/'")
        self.assertLess(fallback, install)
        self.assertLess(install, activate)
        self.assertIn("repair_recovery_entry", script)
        self.assertIn("sun60i-a733-cubie-a7z.dtb", script)
        self.assertIn("module_blacklist=pvrsrvkm", script)

    def test_hdmi_hotplug_patch_preserves_drm_atomic_state(self) -> None:
        patch = (
            ROOT
            / "patches/a733-bsp/0002-drm-hdmi-keep-atomic-state-across-hpd.patch"
        ).read_text()

        self.assertIn("_sunxi_drv_hdmi_hpd_plugout", patch)
        self.assertIn("Keep the hardware state synchronized", patch)
        self.assertIn("-\tret = _sunxi_drv_hdmi_disable(hdmi)", patch)
        self.assertIn("-\thdmi->hdmi_ctrl.drm_enable", patch)

    def test_display_package_advances_for_hotplug_fix(self) -> None:
        script = (ROOT / "tools/package_a733_kernel_display.sh").read_text()

        self.assertIn("5.15.147-21.1+display3", script)
        self.assertIn("INPUT.deb A7Z.dtb OUTPUT.deb", script)
        self.assertIn("sun60i-a733-cubie-a7z.dtb", script)
        self.assertIn('install -D -m 0644 "$dtb"', script)

    def test_display_deployment_preserves_recovery_entry(self) -> None:
        script = (ROOT / "tools/deploy_a733_display_kernel.sh").read_text()

        self.assertIn("repair_recovery_entry", script)
        self.assertIn("sun60i-a733-cubie-a7z.dtb", script)
        self.assertIn("module_blacklist=pvrsrvkm", script)


if __name__ == "__main__":
    unittest.main()
