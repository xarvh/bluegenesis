module App exposing (..)

import AnimationFrame
import Html exposing (Html)
import Time exposing (Time)
import WebGL exposing (Renderable)


type alias Generation =
    List String


type alias Model =
    { generations : List Generation
    , time : Time
    }


scene : Model -> List Renderable
scene model =
    []


type Msg
    = AnimationFrameTriggers Time


view : Model -> Html Msg
view model =
    model
        |> scene
        |> WebGL.toHtml []


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        AnimationFrameTriggers dt ->
            ( { model | time = dt + model.time }, Cmd.none )


main : Program Never Model Msg
main =
    Html.program
        { init = ( Model [] 0, Cmd.none )
        , view = view
        , update = update
        , subscriptions = \model -> AnimationFrame.diffs AnimationFrameTriggers
        }
