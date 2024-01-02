import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import*
import numpy as np
from ctypes import *
from OpenGL.GL.shaders import compileProgram, compileShader
import imgui
from imgui.integrations.glfw import GlfwRenderer
from PIL import Image
import pyrr

def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compile and link shader modules to make a shader program.

        Parameters:

            vertex_filepath: path to the text file storing the vertex
                            source code
            
            fragment_filepath: path to the text file storing the
                                fragment source code
        
        Returns:

            A handle to the created shader program
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

class App:
    def __init__(self):
        if not glfw.init():
            print("Failed to init GLFW")
            return
        self.ScreenWidth = 1280
        self.ScreenHeight = 900
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)
        self.window = glfw.create_window(self.ScreenWidth, self.ScreenHeight, "Hello World", None, None)
        window = self.window
        if not self.window:
            glfw.terminate()
            return
        
        glfw.make_context_current(self.window)
        glClearColor(0.1, 0.2, 0.2, 1)
        self.shader = self.CreateShader("Shaders/vertex.txt", "Shaders/fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        self.texture = Material("Textures/container2.png")
        glEnable(GL_DEPTH_TEST)
        
        self._create_assets()

        self._set_onetime_uniforms()

        self._get_uniform_locations()

        imgui.create_context()
        self.io = imgui.get_io()
        self.io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
        self.impl = GlfwRenderer(self.window)
        self.show_custom_window = True

        self.mainLoop()
    def _create_assets(self) -> None:
        """
        Create all of the assets needed for drawing.
        """
        self.cube = Entity(
        position = [0,0,-3],
        eulers = [0,0,0]
        )
        self.cube_mesh = Mesh("Models/sphere.obj")
        self.shader = create_shader(
            vertex_filepath = "Shaders/vertex.txt", 
            fragment_filepath = "Shaders/fragment.txt")
    def _set_onetime_uniforms(self) -> None:
        """
            Some shader data only needs to be set once.
        """

        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = self.ScreenWidth/self.ScreenHeight, 
            near = 0.1, far = 1000, dtype=np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, projection_transform
        )

    def _get_uniform_locations(self) -> None:
        """
            Query and store the locations of shader uniforms
        """

        glUseProgram(self.shader)
        self.modelMatrixLocation = glGetUniformLocation(self.shader,"model")

    def mainLoop(self):
        running = True
        # Loop until the user closes the window
        while(running and not glfw.window_should_close(self.window)):
        # Render here, e.g. using pyOpenGL
            glfw.poll_events()
            self.impl.process_inputs()
            #update cube
            self.cube.update()
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)

            
            glUniformMatrix4fv(
                self.modelMatrixLocation, 1, GL_FALSE, 
                self.cube.get_model_transform())
            self.texture.use()
            self.cube_mesh.arm_for_drawing()
            self.cube_mesh.draw()
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

            #imgui.show_test_window()
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
    def docking_space(self, name: str):
        flags = (imgui.WINDOW_MENU_BAR 
        | imgui.WINDOW_NO_DOCKING 
        # | imgui.WINDOW_NO_BACKGROUND
        | imgui.WINDOW_NO_TITLE_BAR
        | imgui.WINDOW_NO_COLLAPSE
        | imgui.WINDOW_NO_RESIZE
        | imgui.WINDOW_NO_MOVE
        | imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS
        | imgui.WINDOW_NO_NAV_FOCUS
        )

        viewport = imgui.get_main_viewport()
        x, y = viewport.pos
        w, h = viewport.size
        imgui.set_next_window_position(x, y)
        imgui.set_next_window_size(w, h)
        # imgui.set_next_window_viewport(viewport.id)
        imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.0)
        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0.0)

        # When using ImGuiDockNodeFlags_PassthruCentralNode, DockSpace() will render our background and handle the pass-thru hole, so we ask Begin() to not render a background.
        # local window_flags = self.window_flags
        # if bit.band(self.dockspace_flags, ) ~= 0 then
        #     window_flags = bit.bor(window_flags, const.ImGuiWindowFlags_.NoBackground)
        # end

        # Important: note that we proceed even if Begin() returns false (aka window is collapsed).
        # This is because we want to keep our DockSpace() active. If a DockSpace() is inactive,
        # all active windows docked into it will lose their parent and become undocked.
        # We cannot preserve the docking relationship between an active window and an inactive docking, otherwise
        # any change of dockspace/settings would lead to windows being stuck in limbo and never being visible.
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0, 0))
        imgui.begin(name, None, flags)
        imgui.pop_style_var()
        imgui.pop_style_var(2)

        # DockSpace
        dockspace_id = imgui.get_id(name)
        imgui.dockspace(dockspace_id, (0, 0), imgui.DOCKNODE_PASSTHRU_CENTRAL_NODE)

        imgui.end()

    def Imgui_Frame(self):
        
        imgui.new_frame()

        self.docking_space('docking_space')

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        if show_custom_window:
            is_expand, show_custom_window = imgui.begin("Custom window", True)
            if is_expand:
                imgui.text("Bar")
                imgui.text_ansi("B\033[31marA\033[mnsi ")
                imgui.text_ansi_colored("Eg\033[31mgAn\033[msi ", 0.2, 1., 0.)
                imgui.extra.text_ansi_colored("Eggs", 0.2, 1., 0.)
            imgui.end()

        show_test_window()
        # imgui.show_test_window()

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
    


class CubeMesh:
    """
        Used to draw a cube.
    """

    def __init__(self):

        # x, y, z, s, t
        vertices = (
            -0.5, -0.5, -0.5, 0, 0,
             0.5, -0.5, -0.5, 1, 0,
             0.5,  0.5, -0.5, 1, 1,

             0.5,  0.5, -0.5, 1, 1,
            -0.5,  0.5, -0.5, 0, 1,
            -0.5, -0.5, -0.5, 0, 0,

            -0.5, -0.5,  0.5, 0, 0,
             0.5, -0.5,  0.5, 1, 0,
             0.5,  0.5,  0.5, 1, 1,

             0.5,  0.5,  0.5, 1, 1,
            -0.5,  0.5,  0.5, 0, 1,
            -0.5, -0.5,  0.5, 0, 0,

            -0.5,  0.5,  0.5, 1, 0,
            -0.5,  0.5, -0.5, 1, 1,
            -0.5, -0.5, -0.5, 0, 1,

            -0.5, -0.5, -0.5, 0, 1,
            -0.5, -0.5,  0.5, 0, 0,
            -0.5,  0.5,  0.5, 1, 0,

             0.5,  0.5,  0.5, 1, 0,
             0.5,  0.5, -0.5, 1, 1,
             0.5, -0.5, -0.5, 0, 1,

             0.5, -0.5, -0.5, 0, 1,
             0.5, -0.5,  0.5, 0, 0,
             0.5,  0.5,  0.5, 1, 0,

            -0.5, -0.5, -0.5, 0, 1,
             0.5, -0.5, -0.5, 1, 1,
             0.5, -0.5,  0.5, 1, 0,

             0.5, -0.5,  0.5, 1, 0,
            -0.5, -0.5,  0.5, 0, 0,
            -0.5, -0.5, -0.5, 0, 1,

            -0.5,  0.5, -0.5, 0, 1,
             0.5,  0.5, -0.5, 1, 1,
             0.5,  0.5,  0.5, 1, 0,

             0.5,  0.5,  0.5, 1, 0,
            -0.5,  0.5,  0.5, 0, 0,
            -0.5,  0.5, -0.5, 0, 1
        )
        self.vertex_count = len(vertices)//5
        vertices = np.array(vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
    
    def arm_for_drawing(self) -> None:
        """
            Arm the triangle for drawing.
        """
        glBindVertexArray(self.vao)
    
    def draw(self) -> None:
        """
            Draw the triangle.
        """

        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Mesh:
    def __init__(self, filename):

        vertices = self.loadmesh(filename)
        self.vertex_count = len(vertices)//8
        vertices = np.array(vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
    def loadmesh(self, filename: str) -> list[float]:
        v = []
        vt = []
        vn = []

        vertices = []

        with open(filename, "r") as file:
            line = file.readline()

            while line:
            
                words = line.split(" ")
                if words[0] == "v":
                    v.append(self.read_vertex_data(words))
                elif words[0] == "vt":
                    vt.append(self.read_TexCoords_data(words))
                elif words[0] == "vn":
                    vn.append(self.read_normal_data(words))
                elif words[0] == "f":
                    self.read_face_data(words, v, vt, vn, vertices)
                line = file.readline()

        return vertices

    def read_vertex_data(self, words: list[str]) -> list[float]:
        return [float(words[1]), float(words[2]), float(words[3])] 
    def read_TexCoords_data(self, words: list[str]) -> list[float]:
        return [float(words[1]), float(words[2])] 
    def read_normal_data(self, words: list[str]) -> list[float]:
        return [float(words[1]), float(words[2]), float(words[3])] 
    def read_face_data(self, words: list[str], v: list[list[float]], vt: list[list[float]], vn: list[list[float]], vertices: list[float]) -> None:
        triangleCount = len(words) - 3

        for i in range(triangleCount):
            self.make_corner(words[1], v, vt, vn, vertices)
            self.make_corner(words[2 + i], v, vt, vn, vertices)
            self.make_corner(words[3 + i], v, vt, vn, vertices)

    def make_corner(self, cornerdescription: str, v: list[list[float]], vt: list[list[float]], vn: list[list[float]], vertices: list[float]) -> None:

        v_vt_vn = cornerdescription.split("/")

        for element in v[int(v_vt_vn[0]) -1 ]:
            vertices.append(element)
        for element in vt[int(v_vt_vn[1]) -1 ]:
            vertices.append(element)
        for element in vn[int(v_vt_vn[2]) -1 ]:
            vertices.append(element)
    def arm_for_drawing(self) -> None:
        """
            Arm the triangle for drawing.
        """
        glBindVertexArray(self.vao)
    
    def draw(self) -> None:
        """
            Draw the triangle.
        """

        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))

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
        
class Entity:
    """
        A basic object in the world, with a position and rotation.
    """


    def __init__(self, position: list[float], eulers: list[float]):
        """
            Initialize the entity.

            Parameters:

                position: the position of the entity.

                eulers: the rotation of the entity
                        about each axis.
        """

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
    
    def update(self) -> None:
        """
            Update the object, this is hard coded for now.
        """

        self.eulers[1] += 0.25
        
        if self.eulers[1] > 360:
            self.eulers[1] -= 360

    def get_model_transform(self) -> np.ndarray:
        """
            Returns the entity's model to world
            transformation matrix.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis = [0, 1, 0],
                theta = np.radians(self.eulers[1]), 
                dtype = np.float32
            )
        )

        return pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )


def main():
    app = App()

    

if __name__ == "__main__":
    main()