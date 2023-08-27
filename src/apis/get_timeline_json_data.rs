use mongodb::{
        sync::Client,
        error::Result,
};
use config::*;
use std::collections::HashMap;

use rustc_serialize::json;
use serde::{Deserialize, Serialize};
use serde_json;

#[derive(Debug, Serialize, Deserialize)]
struct Json {
        json_timeline: String,
}

pub fn get_timeline_json_data() -> Result<std::string::String> {

    let mut settings = Config::default();
    settings.merge(File::with_name("config")).unwrap();
    let conf = settings.try_into::<HashMap<String, String>>().unwrap();

    let mut url =  String::from("mongodb://");
    url.push_str(conf.get("mongo_user").unwrap());
    url.push(':');
    url.push_str(conf.get("mongo_password").unwrap());
    url.push('@');
    url.push_str(conf.get("mongo_db").unwrap());
                                                                    

    let client = Client::with_uri_str(url)?;
    let db = client.database(conf.get("mongo_name").unwrap());
    let collection = db.collection::<Json>("timeline_json");

    // Query the collection and retrieve the documents as a cursor
    let cursor = collection.find(None, None)?;

    // Iterate through the cursor and convert each document to a JSON string
    let mut results = Vec::new();

    for result in cursor {
        let document = result?;
        results.push(document.json_timeline);
    }
                             
    return Ok(results.into_iter().collect());
}
