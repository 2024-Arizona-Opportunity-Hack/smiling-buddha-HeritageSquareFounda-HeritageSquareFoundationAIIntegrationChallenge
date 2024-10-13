
import * as path from 'path';

import {
    // Document,
    IngestionPipeline,
    // MetadataMode,
    OpenAIEmbedding,
    TitleExtractor,
    QdrantVectorStore,
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    OpenAI,
    MetadataMode,
    MarkdownNodeParser,
  } from "llamaindex";

import {AddFileName} from "./add-title.transformer";

import { QdrantClient } from "@qdrant/js-client-rest";
import * as dotenv from 'dotenv';
import { getfiles, downloadFileContent } from '../google-drive-helper/gdrive.helper';
dotenv.config();



Settings.llm = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  model: "gpt-3.5-turbo",
  temperature : 0.3
})

const client = new QdrantClient({
  host: process.env.QDRANT_ENDPOINT,
  apiKey: process.env.QDRANT_API_KEY,
});

const vectorStore = new QdrantVectorStore({
  collectionName: "Heritage_Square",
  client : client
});

export const qdrant_ingestion = async(metadata) =>{

  const pipeline = new IngestionPipeline({
    transformations: [
      new MarkdownNodeParser(),
      // new AddFileName(),
      new TitleExtractor(),
      new OpenAIEmbedding(),
    ],
    vectorStore,
  });

    const directoryPath = path.resolve(__dirname, '../google-drive-helper/fileDownload');
    
    let documents = await new SimpleDirectoryReader().loadData({directoryPath : directoryPath});
    // @ts-ignore
    documents = documents.map((doc, index) => {

      const obj = {
        "gDrive_DocID" : metadata.file_id,
        "dDrive_DocName" : metadata.file_name,
        "dDrive_DocLink" : metadata.link,
        "dDrive_DocType" : metadata.file_type,
      }
      doc.metadata = {
        ...doc.metadata,
        custom_metadata : obj

      }
      return doc;
    });


    console.log(documents)
    // console.log("now running pipeline")
    const nodes = await pipeline.run({ documents: documents });

    const index = VectorStoreIndex.fromVectorStore(vectorStore);


    // print out the result of the pipeline run
  for (const node of nodes) {
    console.log(node.getContent(MetadataMode.NONE));
  }



}




export const processfiles = async ()=>{

    let fileDict = await getfiles();

    // console.log(fileDict)
    // console.log("\nFile details dictionary:");
        // for (const [fileId, details] of Object.entries(fileDict)) {
        //     console.log(`${fileId}: ${JSON.stringify(details)}`);
        // }

        for (const [fileId, details] of Object.entries(fileDict)) {
          // @ts-ignore
            await downloadFileContent(details.file_id, details.file_name);
            // break;
            await qdrant_ingestion(fileDict[fileId]);
        }
}

processfiles().catch(console.error);
// qdrant_ingestion({
//   "file_id": "1NzPjVu1atrOQ4OSytfmZoKXgUVvMEFqP",
//   "file_name": "2019 G&J one page Sponsor Letter.pdf",
//   "link": "https://drive.google.com/file/d/1NzPjVu1atrOQ4OSytfmZoKXgUVvMEFqP/view?usp=drivesdk",
//   "file_type": "application/pdf"
// }).catch(console.error);