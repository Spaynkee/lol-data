use mongodb::{
        sync::Client,
        error::Result,
};

use rustc_serialize::json;
use serde::{Deserialize, Serialize};
use serde_json;

#[derive(Debug, Serialize, Deserialize)]
struct Json {
        json_data: String,
}

pub fn get_json_data() -> Result<std::string::String> {

    let client = Client::with_uri_str("mongodb://paul:lalala22@192.168.1.3:27019")?;
    let db = client.database("lstats_p_mongo");
    let collection = db.collection::<Json>("json");

    // Query the collection and retrieve the documents as a cursor
    let cursor = collection.find(None, None)?;

    // Iterate through the cursor and convert each document to a JSON string
    let mut results = Vec::new();

    for result in cursor {
        let document = result?;
        results.push(document.json_data);
    }
                             
    return Ok(results.into_iter().collect());
}
