extern crate actix_files;
use actix_web::{middleware, web, App, HttpRequest, HttpServer};
use actix_files::Files;
mod get_team_data;
use get_team_data::get_team_data;

use std::path::PathBuf;

//I can write functions that return stuff? so
//if I have a function call another program, one that does sql, then just returns it as a json
//formatted string, then we're good?
//async fn index(req: HttpRequest) -> &'static str {
//async fn index() -> &'static str {
async fn index() -> std::string::String {
    get_team_data()
}

#[actix_rt::main]
async fn main() -> std::io::Result<()> {
    std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            // enable logger
            .wrap(middleware::Logger::default())
            .service(web::resource("/index.html").to(|| async { "Is this changed?" }))
            .service(web::resource("/api/get_team_data").to(index))
            .service(Files::new("/", "./build").index_file("index.html"))
            //These are two different routes established.
    })
    .bind("127.0.0.1:5000")?
    .run()
    .await
}
