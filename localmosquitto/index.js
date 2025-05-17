// server.ts or index.ts
import express from "express";
import bodyParser from "body-parser";
import mqtt from "mqtt";
import cors from "cors";

// Setup Express app
const app = express();
const port = 3000;

var counter = 0;
var activeBoatList = [];

// BOAT-1: MAC: "A4:CF:12:B4:06:66"
// BOAT-2: MAC: "A4:CF:12:BF:53:CE"
// BOAT-3 MAC:  "A4:CF:12:B4:06:9F"

const boatOneMac = "A4:CF:12:B4:06:66";
const boatTWOeMac = "A4:CF:12:BF:53:CE";
const boatThreeMac = "A4:CF:12:B4:06:9F";

app.use(cors());

app.use(bodyParser.urlencoded({ extended: true }));

// MQTT Credentials
const MQTT_HOST = "ca403c7db33f468fbc8fa41f694c6f4d.s1.eu.hivemq.cloud";
const MQTT_PORT = 8883;
const MQTT_USERNAME = "nicklasjeppesen";
const MQTT_PASSWORD = "Xujme3-zefrid-reqjyq";

// MQTT connection options
const options = {
  host: MQTT_HOST,
  port: MQTT_PORT,
  protocol: "mqtts",
  username: MQTT_USERNAME,
  password: MQTT_PASSWORD,
  rejectUnauthorized: true, // verify certificate
};

// Connect to MQTT broker
const client = mqtt.connect(options);

let lastConnectMsg = {}; // connected message from esp

client.on("connect", () => {
  console.log("✅ Connected to HiveMQ Cloud MQTT broker");
  client.subscribe("connected", (err) => {
    if (err) {
      console.error("❌ Failed to subscribe to topic:", err);
    }
  });
});

client.on("error", (err) => {
  console.error("❌ MQTT connection error:", err);
});

client.on("message", (topic, message) => {
  if (topic === "connected") {
    const msg = JSON.parse(message.toString());
    lastConnectMsg = msg;
    console.log("📥 Received connected message:", msg);

    counter = counter + 1;
    //const label = "Boat: " + counter.toString();
    const mac = msg["MAC"];

    // Check if mac already exists in activeBoatList
    const macExists = activeBoatList.some((item) => item.mac === mac);
    var label = "";
    if (mac == boatOneMac) {
      label = "Boat: 1";
    } else if (mac == boatTWOeMac) {
      label = "Boat: 2";
    } else if (mac == boatThreeMac) {
      label = "Boat: 3";
    }

    if (!macExists) {
      activeBoatList.push({ label, mac });
    } else {
      console.log(`MAC address ${mac} already exists in the list.`);
    }
  }
});

// Endpoint to receive data and publish to MQTT
app.post("/send-data", (req, res) => {
  const { rightMotor, leftMotor } = req.body;

  const payload = {
    rightMotor: parseInt(rightMotor, 10),
    leftMotor: parseInt(leftMotor, 10),
  };

  console.log("📥 Received data:", payload);

  client.publish("boats/motors", JSON.stringify(payload), (err) => {
    if (err) {
      console.error("❌ Failed to publish:", err);
      return res.status(500).send("Failed to send to MQTT");
    }

    res.send("🚀 Data sent to MQTT broker!");
  });
});

// Endpoint to receive data and publish to MQTT
app.post("/start", (req, res) => {
  console.log("📥 starting:");

  client.publish("boats/motors-start", JSON.stringify(""), (err) => {
    if (err) {
      console.error("❌ Failed to publish:", err);
      return res.status(500).send("Failed to send to MQTT");
    }

    res.send("🚀 Data sent to MQTT broker!");
  });
});

// Endpoint to receive data and publish to MQTT
app.post("/send-setup-data", (req, res) => {
  const { rightMotor, leftMotor, mac } = req.body;

  const payload = {
    rightMotor: parseInt(rightMotor, 10),
    leftMotor: parseInt(leftMotor, 10),
    mac: mac,
  };

  console.log("📥 Received data:", payload);

  client.publish("boats/motorSetup", JSON.stringify(payload), (err) => {
    if (err) {
      console.error("❌ Failed to publish:", err);
      return res.status(500).send("Failed to send to MQTT");
    }

    res.send("🚀 Data sent to MQTT broker!");
  });
});

// Endpoint to calibrate boat speed onn flu to MQTT
app.post("/calibrate", (req, res) => {
  const { rightMotor, leftMotor, mac } = req.body;

  const payload = {
    rightMotor: parseInt(rightMotor, 10),
    leftMotor: parseInt(leftMotor, 10),
    mac: mac,
  };

  console.log("📥 Received data:", payload);

  client.publish("boats/motorsCalibration", JSON.stringify(payload), (err) => {
    if (err) {
      console.error("❌ Failed to publish:", err);
      return res.status(500).send("Failed to send to MQTT");
    }

    res.send("🚀 Data sent to MQTT broker!");
  });
});

app.get("/config", (req, res) => {
  return res.json(lastConnectMsg);
});

app.get("/activboat", (req, res) => {
  return res.json(activeBoatList);
});

app.listen(port, () => {
  console.log(`🌐 Server listening at http://localhost:${port}`);
});
