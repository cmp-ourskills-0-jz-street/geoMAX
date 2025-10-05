#include <WiFi.h>
#include <HTTPClient.h>
#include <esp_now.h>
#include <esp_wifi.h> 
#include <ArduinoJson.h>
#include <map> 

const char* wifiSSID = "corpnet";  
const char* wifiPassword = "hornet228"; 
const String serverUrl = "http://10.37.152.60:8000";  

String myID; 

uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

std::map<String, int> neighbors;

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));

  long randNum = 44444442;
  myID = String(randNum);

  WiFi.begin(wifiSSID, wifiPassword);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected, IP: " + WiFi.localIP().toString());

  WiFi.mode(WIFI_STA);
  //esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_LR);
  //esp_wifi_config_espnow_rate(WIFI_IF_STA, WIFI_PHY_RATE_1M_L); 

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed!");
    while (1);
  }

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add broadcast peer");
  }

  esp_now_register_recv_cb(OnDataRecv);

  if (create()) {
    Serial.println("Created successfully");
  } else {
    Serial.println("Create failed");
    while (1);
  }
}

void OnDataRecv(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  char buffer[32];
  memcpy(buffer, incomingData, len);
  buffer[len] = '\0';
  String receivedID = String(buffer);

  int rssi = info->rx_ctrl->rssi;
  Serial.println("Received from " + receivedID + ", RSSI: " + String(rssi));

  if (receivedID != myID) {
    if (neighbors.find(receivedID) == neighbors.end()) {
      //if (access(receivedID)) {
        neighbors[receivedID] = rssi;
      //} else {
       // Serial.println("Access denied for " + receivedID);
      //}
    } else {
      neighbors[receivedID] = rssi;  
    }
  }
}

bool create() {
  HTTPClient http;
  http.begin(serverUrl + "/create");
  http.addHeader("Content-Type", "application/json");

  DynamicJsonDocument doc(1024);
  doc["id"] = myID;
  String json;
  serializeJson(doc, json);

  int httpCode = http.POST(json);
  //int httpCode = http.GET();
  Serial.println(httpCode);
  return (httpCode == 200);
}

bool access(String seenID) {
  HTTPClient http;
  http.begin(serverUrl + "/access");
  http.addHeader("Content-Type", "application/json");

  DynamicJsonDocument doc(1024);
  doc["my_id"] = myID;
  doc["seen_id"] = seenID;
  String json;
  serializeJson(doc, json);

  int httpCode = http.POST(json);
  if (httpCode == 200) {
    return true;
  }
  return false;
}

void update() {
  std::vector<std::pair<String, int>> topNeighbors;
  for (auto& pair : neighbors) {
    topNeighbors.push_back(pair);
  }
  std::sort(topNeighbors.begin(), topNeighbors.end(), [](const auto& a, const auto& b) {
    return a.second > b.second; 
  });
  if (topNeighbors.size() > 3) topNeighbors.resize(3);

  if (topNeighbors.empty()) return;

  HTTPClient http;
  http.begin(serverUrl + "/update");
  http.addHeader("Content-Type", "application/json");

  DynamicJsonDocument doc(1024);
  doc["id"] = myID;
  JsonObject neighObj = doc.createNestedObject("neighbors");
  for (auto& pair : topNeighbors) {
    neighObj[pair.first] = pair.second;
  }
  String json;
  serializeJson(doc, json);

  int httpCode = http.POST(json);
  if (httpCode == 200) {
    Serial.println("Update sent");
  }
}

void loop() {
  delay(random(0, 1000)); 
  esp_now_send(broadcastAddress, (uint8_t *)myID.c_str(), myID.length());

  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 10000) {
    update();
    lastUpdate = millis();
  }

  delay(100);
}