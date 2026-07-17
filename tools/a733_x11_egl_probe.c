#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <stdlib.h>

static const char *egl_error_name(EGLint error)
{
    switch (error) {
    case EGL_SUCCESS: return "EGL_SUCCESS";
    case EGL_NOT_INITIALIZED: return "EGL_NOT_INITIALIZED";
    case EGL_BAD_ACCESS: return "EGL_BAD_ACCESS";
    case EGL_BAD_ALLOC: return "EGL_BAD_ALLOC";
    case EGL_BAD_ATTRIBUTE: return "EGL_BAD_ATTRIBUTE";
    case EGL_BAD_CONFIG: return "EGL_BAD_CONFIG";
    case EGL_BAD_CONTEXT: return "EGL_BAD_CONTEXT";
    case EGL_BAD_CURRENT_SURFACE: return "EGL_BAD_CURRENT_SURFACE";
    case EGL_BAD_DISPLAY: return "EGL_BAD_DISPLAY";
    case EGL_BAD_MATCH: return "EGL_BAD_MATCH";
    case EGL_BAD_NATIVE_PIXMAP: return "EGL_BAD_NATIVE_PIXMAP";
    case EGL_BAD_NATIVE_WINDOW: return "EGL_BAD_NATIVE_WINDOW";
    case EGL_BAD_PARAMETER: return "EGL_BAD_PARAMETER";
    case EGL_BAD_SURFACE: return "EGL_BAD_SURFACE";
    default: return "unknown";
    }
}

static void report_error(const char *operation)
{
    EGLint error = eglGetError();
    printf("  %-24s failed: %s (0x%04x)\n",
           operation, egl_error_name(error), error);
}

int main(void)
{
    static const EGLint context_attributes[] = {
        EGL_CONTEXT_CLIENT_VERSION, 2,
        EGL_NONE
    };
    static const EGLint pbuffer_attributes[] = {
        EGL_WIDTH, 64,
        EGL_HEIGHT, 64,
        EGL_NONE
    };
    Display *xdisplay = XOpenDisplay(NULL);
    if (!xdisplay) {
        fprintf(stderr, "XOpenDisplay failed\n");
        return 1;
    }

    PFNEGLGETPLATFORMDISPLAYPROC get_platform_display =
        (PFNEGLGETPLATFORMDISPLAYPROC)eglGetProcAddress("eglGetPlatformDisplay");
    if (!get_platform_display) {
        fprintf(stderr, "eglGetPlatformDisplay is unavailable\n");
        XCloseDisplay(xdisplay);
        return 1;
    }

    EGLDisplay display = get_platform_display(
        EGL_PLATFORM_X11_KHR, xdisplay, NULL);
    EGLint major = 0;
    EGLint minor = 0;
    if (display == EGL_NO_DISPLAY || !eglInitialize(display, &major, &minor)) {
        report_error("eglInitialize");
        XCloseDisplay(xdisplay);
        return 1;
    }
    if (!eglBindAPI(EGL_OPENGL_ES_API)) {
        report_error("eglBindAPI");
        eglTerminate(display);
        XCloseDisplay(xdisplay);
        return 1;
    }

    EGLint config_count = 0;
    if (!eglGetConfigs(display, NULL, 0, &config_count) || config_count <= 0) {
        report_error("eglGetConfigs(count)");
        eglTerminate(display);
        XCloseDisplay(xdisplay);
        return 1;
    }
    EGLConfig *configs = calloc((size_t)config_count, sizeof(*configs));
    if (!configs || !eglGetConfigs(display, configs, config_count, &config_count)) {
        report_error("eglGetConfigs(list)");
        free(configs);
        eglTerminate(display);
        XCloseDisplay(xdisplay);
        return 1;
    }

    printf("EGL %d.%d vendor=%s configs=%d\n", major, minor,
           eglQueryString(display, EGL_VENDOR), config_count);
    int tested = 0;
    int window_successes = 0;
    int render_successes = 0;
    int renderer_reported = 0;
    for (EGLint i = 0; i < config_count; ++i) {
        EGLint config_id = 0;
        EGLint surface_type = 0;
        EGLint renderable_type = 0;
        EGLint visual_id = 0;
        eglGetConfigAttrib(display, configs[i], EGL_CONFIG_ID, &config_id);
        eglGetConfigAttrib(display, configs[i], EGL_SURFACE_TYPE, &surface_type);
        eglGetConfigAttrib(display, configs[i], EGL_RENDERABLE_TYPE,
                           &renderable_type);
        eglGetConfigAttrib(display, configs[i], EGL_NATIVE_VISUAL_ID, &visual_id);
        if (!(surface_type & EGL_WINDOW_BIT) ||
            !(renderable_type & EGL_OPENGL_ES2_BIT)) {
            continue;
        }
        ++tested;
        printf("config=0x%02x visual=0x%x surfaces=0x%x\n",
               config_id, visual_id, surface_type);

        EGLContext context = eglCreateContext(
            display, configs[i], EGL_NO_CONTEXT, context_attributes);
        if (context == EGL_NO_CONTEXT) {
            report_error("eglCreateContext");
            continue;
        }

        EGLSurface pbuffer = eglCreatePbufferSurface(
            display, configs[i], pbuffer_attributes);
        if (pbuffer == EGL_NO_SURFACE) {
            report_error("eglCreatePbufferSurface");
        } else if (!eglMakeCurrent(display, pbuffer, pbuffer, context)) {
            report_error("eglMakeCurrent(pbuffer)");
        } else {
            printf("  %-24s ok\n", "eglMakeCurrent(pbuffer)");
            eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE,
                           EGL_NO_CONTEXT);
        }
        if (pbuffer != EGL_NO_SURFACE)
            eglDestroySurface(display, pbuffer);

        XVisualInfo visual_template = {0};
        visual_template.visualid = (VisualID)visual_id;
        int visual_count = 0;
        XVisualInfo *visual = XGetVisualInfo(
            xdisplay, VisualIDMask, &visual_template, &visual_count);
        if (!visual || visual_count == 0) {
            printf("  %-24s failed for visual 0x%x\n",
                   "XGetVisualInfo", visual_id);
            XFree(visual);
            eglDestroyContext(display, context);
            continue;
        }

        XSetWindowAttributes attributes = {0};
        attributes.colormap = XCreateColormap(
            xdisplay, RootWindow(xdisplay, visual->screen), visual->visual,
            AllocNone);
        attributes.border_pixel = 0;
        Window window = XCreateWindow(
            xdisplay, RootWindow(xdisplay, visual->screen), 0, 0, 64, 64, 0,
            visual->depth, InputOutput, visual->visual,
            CWBorderPixel | CWColormap, &attributes);
        XMapWindow(xdisplay, window);
        XSync(xdisplay, False);

        EGLSurface surface = eglCreateWindowSurface(
            display, configs[i], (EGLNativeWindowType)window, NULL);
        if (surface == EGL_NO_SURFACE) {
            report_error("eglCreateWindowSurface");
        } else if (!eglMakeCurrent(display, surface, surface, context)) {
            report_error("eglMakeCurrent(window)");
        } else {
            printf("  %-24s ok\n", "eglMakeCurrent(window)");
            ++window_successes;
            if (!renderer_reported) {
                printf("  GLES vendor=%s renderer=%s version=%s\n",
                       glGetString(GL_VENDOR), glGetString(GL_RENDERER),
                       glGetString(GL_VERSION));
                renderer_reported = 1;
            }
            glClearColor(0.125f, 0.25f, 0.5f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);
            glFinish();
            if (!eglSwapBuffers(display, surface)) {
                report_error("eglSwapBuffers");
            } else {
                printf("  %-24s ok\n", "GLES clear and swap");
                ++render_successes;
            }
            eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE,
                           EGL_NO_CONTEXT);
        }

        if (surface != EGL_NO_SURFACE)
            eglDestroySurface(display, surface);
        XDestroyWindow(xdisplay, window);
        XFreeColormap(xdisplay, attributes.colormap);
        XFree(visual);
        eglDestroyContext(display, context);
    }

    printf("summary: tested=%d window_successes=%d render_successes=%d\n",
           tested, window_successes, render_successes);
    free(configs);
    eglTerminate(display);
    XCloseDisplay(xdisplay);
    return render_successes > 0 ? 0 : 2;
}
