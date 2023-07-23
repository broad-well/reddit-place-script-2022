async function getHistory(x, y, canvas) {
    return await (await fetch("https://gql-realtime-2.reddit.com/query", {
        "headers": {
          "accept": "*/*",
          "accept-language": "en-US,en;q=0.9",
          "apollographql-client-name": "garlic-bread",
          "apollographql-client-version": "0.0.1",
          "authorization": "Bearer [put in your access token]",
          "content-type": "application/json",
          "sec-fetch-dest": "empty",
          "sec-fetch-mode": "cors",
          "sec-fetch-site": "same-site"
        },
        "referrer": "https://garlic-bread.reddit.com/",
        "referrerPolicy": "strict-origin-when-cross-origin",
        "body": "{\"operationName\":\"pixelHistory\",\"variables\":{\"input\":{\"actionName\":\"r/replace:get_tile_history\",\"PixelMessageData\":{\"coordinate\":{\"x\":" + x + ",\"y\":" + y + "},\"colorIndex\":0,\"canvasIndex\":" + canvas + "}}},\"query\":\"mutation pixelHistory($input: ActInput!) {\\n  act(input: $input) {\\n    data {\\n      ... on BasicMessage {\\n        id\\n        data {\\n          ... on GetTileHistoryResponseMessageData {\\n            lastModifiedTimestamp\\n            userInfo {\\n              userID\\n              username\\n              __typename\\n            }\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}",
        "method": "POST",
        "mode": "cors",
        "credentials": "include"
      })).json();
}

async function getBlockHistoryMatrix(canvas, minX, minY, maxX, maxY) {
    const matrix = [];
    for (let y = minY; y <= maxY; ++y) {
        const row = [];
        for (let x = minX; x <= maxX; ++x) {
            const item = (await getHistory(x, y, canvas));
            console.log(item);
            row.push(item.data.act.data[0].data);
        }
        matrix.push(row);
    }
    return matrix;
}

let i = 13;
setInterval(async () => {
    let mat = await getBlockHistoryMatrix(2, 175, 633, 209, 673);
    Deno.writeTextFileSync(`mich-ripbots-${i++}.json`, JSON.stringify(mat));
}, 1000 * 60 * 10);