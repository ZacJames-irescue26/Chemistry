import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import*
import numpy as np
from ctypes import *
from OpenGL.GL.shaders import compileProgram, compileShader
import imgui
from imgui.integrations.glfw import GlfwRenderer
from PIL import Image

class App:
    def __init__(self):
        if not glfw.init():
            print("Failed to init GLFW")
            return
        self.ScreenWidth = 800
        self.ScreenHeight = 600
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)
        self.window = glfw.create_window(640, 480, "Hello World", None, None)
        window = self.window
        if not self.window:
            glfw.terminate()
            return
        
        glfw.make_context_current(self.window)
        glClearColor(0.1, 0.2, 0.2, 1)
        self.shader = self.CreateShader("Shaders/vertex.txt", "Shaders/fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        self.triangle = Triangle()
        self.texture = Material("Textures/container2.png")
        imgui.create_context()
        self.impl = GlfwRenderer(self.window)
        self.show_custom_window = True

        self.mainLoop()

    def mainLoop(self):
        running = True
        # Loop until the user closes the window
        while(running and not glfw.window_should_close(self.window)):
        # Render here, e.g. using pyOpenGL
            glfw.poll_events()
            self.impl.process_inputs()
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.shader)
            self.texture.use()
            glBindVertexArray(self.triangle.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)
            imgui.new_frame()

            if imgui.begin_main_menu_bar():
                if imgui.begin_menu("File", True):

                    clicked_quit, selected_quit = imgui.menu_item(
                        "Quit", "Cmd+Q", False, True
                    )

                    if clicked_quit:
                        sys.exit(0)

                    imgui.end_menu()
                imgui.end_main_menu_bar()

            if self.show_custom_window:
                is_expand, show_custom_window = imgui.begin("Custom window", True)
                if is_expand:
                    imgui.text("Bar")
                    imgui.text_ansi("B\033[31marA\033[mnsi ")
                    imgui.text_ansi_colored("Eg\033[31mgAn\033[msi ", 0.2, 1.0, 0.0)
                    imgui.extra.text_ansi_colored("Eggs", 0.2, 1.0, 0.0)
                imgui.end()

            imgui.show_test_window()
            # imgui.show_test_window()

            imgui.render()
            self.impl.render(imgui.get_draw_data())

        # Swap front and back buffers
            glfw.swap_buffers(self.window)

        # Poll for and process events
            glfw.poll_events()
        quit(self)

    def quit(self):
        self.triangle.destroy
        self.texture.destroy()
        glDeleteProgram(self.shader)
        glfw.terminate()


    def Imgui_Frame(self):
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, selected_quit = imgui.menu_item("Quit", "Cmd+Q", False, True)
                if clicked_quit:
                    sys.exit(0)
                imgui.end_menu()
            imgui.end_main_menu_bar()
        imgui.show_test_window()
        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_colored("Eggs", 0.2, 1.0, 0.0)
        imgui.end()

    def CreateShader(self, vertexFilePath, fragmentFilePath):
        with open(vertexFilePath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragmentFilePath, 'r') as f:
            fragment_src = f.readlines()
        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        return shader
    


class Triangle:
    def __init__(self):
        # x,y,z,r,g,b,s,t
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,
            0.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Material:
    def __init__(self, filenames):

        texture_size = 500
        texture_count = len(filenames)
        #width = 5 * texture_size
        #height = texture_count * texture_size
        #self.textureData = Image.new(mode = "RGBA", size = (width, height))
        for i in range(texture_count):
            with Image.open(f"{filenames}", mode = "r") as img:
                img = img.convert("RGBA")
                width, height = img.size
            ## add more images here
        img_data = bytes(img.tobytes())
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    
    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))
        
def main():
    app = App()


    

if __name__ == "__main__":
    main()