
/*
 * @Date: 2022-8-27 
 * @Description: ESP32 Camera Surveillance Car
 * @FilePath:
 */

#include "esp_camera.h"
#include <WiFi.h>

//
// WARNING!!! Make sure that you have either selected ESP32 Wrover Module,
//            or another board which has PSRAM enabled
//
// Adafruit ESP32 Feather

// Select camera model
//#define CAMERA_MODEL_WROVER_KIT
//#define CAMERA_MODEL_M5STACK_PSRAM
#define CAMERA_MODEL_AI_THINKER

const char *ssid = "STGZ";		   // Enter SSID WIFI Name
const char *password = "15346789"; // Enter WIFI Password

// Define static IP address, gateway, subnet, and DNS
// IPAddress local_IP('192.168.219.101');
// IPAddress gateway(192.168.219.182);
// IPAddress subnet(255.255.255.0); 

#if defined(CAMERA_MODEL_WROVER_KIT)
#define PWDN_GPIO_NUM -1
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 21
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 19
#define Y4_GPIO_NUM 18
#define Y3_GPIO_NUM 5
#define Y2_GPIO_NUM 4
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

#elif defined(CAMERA_MODEL_AI_THINKER)
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

#else
#error "Camera model not selected"
#endif

// GPIO Setting
extern int gpLed = 4; // Light
extern String WiFiAddr = "";

void startCameraServer();

void setup()
{
	Serial.begin(9600);
	Serial.setDebugOutput(true);
	Serial.println();

	pinMode(gpLed, OUTPUT); // Light
	digitalWrite(gpLed, LOW);

	camera_config_t config;
	config.ledc_channel = LEDC_CHANNEL_0;
	config.ledc_timer = LEDC_TIMER_0;
	config.pin_d0 = Y2_GPIO_NUM;
	config.pin_d1 = Y3_GPIO_NUM;
	config.pin_d2 = Y4_GPIO_NUM;
	config.pin_d3 = Y5_GPIO_NUM;
	config.pin_d4 = Y6_GPIO_NUM;
	config.pin_d5 = Y7_GPIO_NUM;
	config.pin_d6 = Y8_GPIO_NUM;
	config.pin_d7 = Y9_GPIO_NUM;
	config.pin_xclk = XCLK_GPIO_NUM;
	config.pin_pclk = PCLK_GPIO_NUM;
	config.pin_vsync = VSYNC_GPIO_NUM;
	config.pin_href = HREF_GPIO_NUM;
	config.pin_sscb_sda = SIOD_GPIO_NUM;
	config.pin_sscb_scl = SIOC_GPIO_NUM;
	config.pin_pwdn = PWDN_GPIO_NUM;
	config.pin_reset = RESET_GPIO_NUM;
	config.xclk_freq_hz = 20000000;
	config.pixel_format = PIXFORMAT_JPEG;
	// init with high specs to pre-allocate larger buffers
	if (psramFound())
	{
		config.frame_size = FRAMESIZE_HVGA;/*	FRAMESIZE_96X96,    // 96x96
												FRAMESIZE_QQVGA,    // 160x120
												FRAMESIZE_QCIF,     // 176x144
												FRAMESIZE_HQVGA,    // 240x176
												FRAMESIZE_240X240,  // 240x240
												FRAMESIZE_QVGA,     // 320x240
												FRAMESIZE_CIF,      // 400x296
												FRAMESIZE_HVGA,     // 480x320
												FRAMESIZE_VGA,      // 640x480
												FRAMESIZE_SVGA,     // 800x600
												FRAMESIZE_XGA,      // 1024x768
												FRAMESIZE_HD,       // 1280x720
												FRAMESIZE_SXGA,     // 1280x1024
												FRAMESIZE_UXGA,     // 1600x1200*/
		config.jpeg_quality = 10;		/*可以是介于 0 和 63 之间的数字。数字越小，质量越高*/
		config.fb_count = 2;
		Serial.println("FRAMESIZE_HVGA");
	}
	else
	{
		config.frame_size = FRAMESIZE_CIF;
		config.jpeg_quality = 12;
		config.fb_count = 1;
		Serial.println("FRAMESIZE_QVGA");
	}

	// camera init
	esp_err_t err = esp_camera_init(&config);
	if (err != ESP_OK)
	{
		Serial.printf("Camera init failed with error 0x%x", err);
		return;
	}

	// drop down frame size for higher initial frame rate
	sensor_t *s = esp_camera_sensor_get();
	s->set_framesize(s, FRAMESIZE_CIF);

	WiFi.begin(ssid, password);

	while (WiFi.status() != WL_CONNECTED)
	{
		delay(500);
		Serial.print(".");
	}
	Serial.println("");
	Serial.println("WiFi connected");

	startCameraServer();

	Serial.print("Camera Ready! Use 'http://");
	Serial.print(WiFi.localIP());
	WiFiAddr = WiFi.localIP().toString();
	Serial.println("' to connect");
}

void loop()
{

	// put your main code here, to run repeatedly:
}
