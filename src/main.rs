extern crate actix_files;
use actix_web::{middleware, web, App, HttpRequest, HttpServer, Result};
use actix_web::http::{StatusCode};
use actix_files::Files;
use actix_files::NamedFile;
use std::pin::Pin;
use std::task::{Context, Poll};
use std::time::Duration;
use actix_web::{HttpResponse, web};
use bytes::Bytes;
use futures_util::stream::Stream;
use opencv::{core, imgcodecs, prelude::*, videoio};

#[path = "apis/get_team_data.rs"] mod get_team_data;
use get_team_data::get_team_data;

#[path = "apis/get_user_data.rs"] mod get_user_data;
use get_user_data::get_user_data;

#[path = "apis/update_data.rs"] mod update_data;
use update_data::update_data;

#[path = "apis/get_script_status.rs"] mod get_script_status;
use get_script_status::get_script_status;

#[path = "apis/get_league_users.rs"] mod get_league_users;
use get_league_users::get_league_users;

#[path = "apis/get_json_data.rs"] mod get_json_data;
use get_json_data::get_json_data;

#[path = "apis/get_timeline_json_data.rs"] mod get_timeline_json_data;
use get_timeline_json_data::get_timeline_json_data;

#[path = "apis/get_items.rs"] mod get_items;
use get_items::get_items;

#[path = "apis/get_script_runs.rs"] mod get_script_runs;
use get_script_runs::get_script_runs;

#[path = "apis/get_champions.rs"] mod get_champions;
use get_champions::get_champions;

#[path = "apis/get_champ_card_data.rs"] mod get_champ_card_data;
use get_champ_card_data::get_champ_card_data;

async fn team_data() -> std::string::String {
    get_team_data()
}

async fn user_data(req: HttpRequest) -> std::string::String {
    get_user_data(req)
}

async fn update() -> std::string::String {
    update_data()
}

async fn script_status() -> std::string::String {
    get_script_status()
}


async fn league_users() -> std::string::String {
    get_league_users()
}

async fn json_data() -> std::string::String {
    get_json_data().unwrap()
}

async fn timeline_json_data() -> std::string::String {
    get_timeline_json_data().unwrap()
}

async fn items() -> std::string::String {
    get_items()
}

async fn script_runs() -> std::string::String {
    get_script_runs()
}

async fn champions() -> std::string::String {
    get_champions()
}

async fn champ_card_data(req: HttpRequest) -> std::string::String {
    get_champ_card_data(req)
}

async fn route_to_index() -> Result<NamedFile> {

    Ok(NamedFile::open("build/index.html")?.set_status_code(StatusCode::NOT_FOUND))
}

struct MjpegStream {
    cam: videoio::VideoCapture,
}

impl MjpegStream {
    fn new() -> Self {
        let mut cam = videoio::VideoCapture::new(0, videoio::CAP_ANY).unwrap(); // webcam index 0
        cam.set(videoio::CAP_PROP_FRAME_WIDTH, 640.0).unwrap();
        cam.set(videoio::CAP_PROP_FRAME_HEIGHT, 480.0).unwrap();
        MjpegStream { cam }
    }
}

impl Stream for MjpegStream {
    type Item = Result<Bytes, actix_web::Error>;

    fn poll_next(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        let mut frame = core::Mat::default();
        if !self.cam.read(&mut frame).unwrap() || frame.size().unwrap().width == 0 {
            return Poll::Ready(None);
        }

        let mut buf = opencv::types::VectorOfu8::new();
        imgcodecs::imencode(".jpg", &frame, &mut buf, &opencv::types::VectorOfi32::new()).unwrap();

        let data = format!(
            "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: {}\r\n\r\n",
            buf.len()
        )
        .into_bytes();

        let mut payload = data;
        payload.extend(buf);

        std::thread::sleep(Duration::from_millis(100)); // ~10 fps

        Poll::Ready(Some(Ok(Bytes::from(payload))))
    }
}

async fn stream_video() -> HttpResponse {
    use actix_web::http::header;

    let stream = MjpegStream::new();
    HttpResponse::Ok()
        .insert_header((header::CONTENT_TYPE, "multipart/x-mixed-replace; boundary=frame"))
        .streaming(stream)
}

#[actix_rt::main]
async fn main() -> std::io::Result<()> {
    std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            // enable logger
            .wrap(middleware::Logger::default())
            .service(web::resource("/api/get_team_data").to(team_data))
            .service(web::resource("/api/get_user_data").to(user_data))
            .service(web::resource("/api/update_data").to(update))
            .service(web::resource("/api/get_script_status").to(script_status))
            .service(web::resource("/api/get_league_users").to(league_users))
            .service(web::resource("/api/get_json_data").to(json_data))
            .service(web::resource("/api/get_timeline_json_data").to(timeline_json_data))
            .service(web::resource("/api/get_items").to(items))
            .service(web::resource("/api/get_script_runs").to(script_runs))
            .service(web::resource("/api/get_champions").to(champions))
            .service(web::resource("/api/get_champ_card_data").to(champ_card_data))
            .service(web::resource("/stream").to(stream_video))
            .service(Files::new("/", "./build").index_file("index.html"))
            .default_service(web::to(route_to_index))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}
