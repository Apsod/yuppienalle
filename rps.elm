import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import WebSocket


main =
  Html.program
    { init = init
    , view = view
    , update = update
    , subscriptions = subscriptions
    }


-- MODEL

type alias Model = List Result


init : (Model, Cmd Msg)
init =
  ([], Cmd.none)


-- UPDATE

type Move
  = Rock
  | Paper
  | Scissor

type Result
  = Win
  | Tie
  | Loss

type Msg
  = Send Move
  | Recieve Result
  | Error


update : Msg -> Model -> (Model, Cmd Msg)
update msg results =
  case msg of
    Send Rock -> (results, WebSocket.send "ws://192.168.10.209:9000" "rock")
    Send Paper -> (results, WebSocket.send "ws://192.168.10.209:9000" "paper")
    Send Scissor -> (results, WebSocket.send "ws://192.168.10.209:9000" "scissor")
    Recieve result -> (result :: results, Cmd.none)
    Error -> (results, Cmd.none)


-- SUBSCRIPTIONS
subscriptions model =
  WebSocket.listen "ws://192.168.10.209:9000" parse

parse : String -> Msg
parse str =
  case str of
    "win" -> Recieve Win
    "tie" -> Recieve Tie
    "loss" -> Recieve Loss
    _ -> Error

-- VIEW

view : Model -> Html Msg
view model =
  div []
    [ div [] (List.map viewMessage model)
    , button [onClick (Send Rock)] [text "Sten!"]
    , button [onClick (Send Scissor)] [text "Sax!"]
    , button [onClick (Send Paper)] [text "Påse!"]
    ]


viewMessage : Result -> Html msg
viewMessage result =
  let txt = case result of
    Win -> "vinst!"
    Tie -> "lika!"
    Loss -> "förlust!"
  in div [] [ text txt ]
