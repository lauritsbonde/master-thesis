// server.ts or index.ts
import express from "express";
import bodyParser from "body-parser";
import mqtt from "mqtt";
import cors from "cors";

// Setup Express app
const app = express();
const port = 3000;

app.use(cors());

app.use(bodyParser.urlencoded({ extended: true }));

// MQTT Credentials
const MQTT_HOST = "8e0273b3631541a2a5d19ce1e57ebdba.s1.eu.hivemq.cloud";
const MQTT_PORT = 8883;
const MQTT_USERNAME = "lauritsbonde";
const MQTT_PASSWORD = "bkDx87$@SL2h5f$^Hw%c";

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

client.on("connect", () => {
  console.log("✅ Connected to HiveMQ Cloud MQTT broker");
});

client.on("error", (err) => {
  console.error("❌ MQTT connection error:", err);
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

app.listen(port, () => {
  console.log(`🌐 Server listening at http://localhost:${port}`);
});
