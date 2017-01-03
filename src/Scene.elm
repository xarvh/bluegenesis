module Scene exposing (..)

import WebGL exposing (Shader, Renderable)
import Math.Vector3 exposing (Vec3)
import Math.Matrix4 exposing (Mat4)


renderables : a -> List Renderable
renderables a =
    []


type alias VertexAttributes =
    { color : Vec3
    , position : Vec3
    }


type alias Uniforms =
    { camera : Mat4
    , perspective : Mat4
    , rotation : Mat4
    }


type alias Varyings =
    { vcolor : Vec3
    }


vertexShader : Shader VertexAttributes Uniforms Varyings
vertexShader =
    [glsl|
      attribute vec3 position;
      attribute vec3 color;

      uniform mat4 camera;
      uniform mat4 perspective;
      uniform mat4 rotation;

      varying vec3 vcolor;

      void main () {
          gl_Position = perspective * camera * rotation * vec4(position, 1.0);
          vcolor = color;
      }
    |]


fragmentShader : Shader {} Uniforms Varyings
fragmentShader =
    [glsl|
      varying vec3 vcolor;

      void main () {
          gl_FragColor = vcolor;
      }
    |]
