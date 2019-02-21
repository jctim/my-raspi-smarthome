PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS thing_alexa_capability_properties;

DROP TABLE IF EXISTS thing;
DROP TABLE IF EXISTS user;

DROP TABLE IF EXISTS alexa_category;
DROP TABLE IF EXISTS alexa_capability;


CREATE TABLE alexa_category (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE alexa_capability (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  amazon_id TEXT NOT NULL,
  user_scope_uuid TEXT NOT NULL
);

CREATE TABLE thing (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  endpoint_id TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  friendly_name TEXT NOT NULL,
  description TEXT DEFAULT '',
  manufacturer_name TEXT DEFAULT '',
  alexa_category_id INTEGER DEFAULT NULL,
  UNIQUE(endpoint_id, user_id) ON CONFLICT REPLACE,
  CONSTRAINT fk_thing_user FOREIGN KEY (user_id) REFERENCES user(id)
  CONSTRAINT fk_thing_alexa_category FOREIGN KEY (alexa_category_id) REFERENCES alexa_category(id)
);

CREATE TABLE thing_alexa_capability_properties (
  thing_id INTEGER NOT NULL,
  alexa_capability_id INTEGER NOT NULL,
  properties TEXT DEFAULT '' -- TODO comma separated list of properties, may differ for each capability 
);

-- default alexa categories (https://developer.amazon.com/docs/device-apis/alexa-discovery.html#display-categories)
INSERT INTO alexa_category(name) VALUES 
  ('ACTIVITY_TRIGGER'), 
  ('CAMERA'),
  ('CONTACT_SENSOR'),
  ('DOOR'),
  ('DOORBELL'),
  ('LIGHT'),
  ('MICROWAVE'),
  ('MOTION_SENSOR'),
  ('OTHER'),
  ('SCENE_TRIGGER'),
  ('SMARTLOCK'),
  ('SMARTPLUG'),
  ('SPEAKER'),
  ('SWITCH'),
  ('TEMPERATURE_SENSOR'),
  ('THERMOSTAT'),
  ('TV');

-- default alexa capabilities (https://developer.amazon.com/docs/device-apis/list-of-interfaces.html)
INSERT INTO alexa_capability(name) VALUES 
  ('Alexa.BrightnessController'),
  ('Alexa.CameraStreamController'),
  ('Alexa.ChannelController'),
  ('Alexa.ColorController'),
  ('Alexa.ColorTemperatureController'),
  ('Alexa.ContactSensor'),
  ('Alexa.Cooking'),
  ('Alexa.Cooking.PresetController'),
  ('Alexa.Cooking.TimeController'),
  ('Alexa.CustomIntent'),
  ('Alexa.DoorbellEventSource'),
  ('Alexa.EndpointHealth'),
  ('Alexa.EqualizerController'),
  ('Alexa.InputController'),
  ('Alexa.LockController'),
  ('Alexa.MediaMetadata'),
  ('Alexa.ModeController'),
  ('Alexa.MotionSensor'),
  ('Alexa.PowerController'),
  ('Alexa.PowerLevelController'),
  ('Alexa.RangeController'),
  ('Alexa.RTCSessionController'),
  ('Alexa.SceneController'),
  ('Alexa.SecurityPanelController'),
  ('Alexa.Speaker'),
  ('Alexa.StepSpeaker'),
  ('Alexa.TemperatureSensor'),
  ('Alexa.ThermostatController'),
  ('Alexa.TimeHoldController'),
  ('Alexa.ToggleController'),
  ('Alexa.WakeOnLANController'),
  ('Alexa.Launcher'),
  ('Alexa.PlaybackController'),
  ('Alexa.PlaybackStateReporter'),
  ('Alexa.RecordController'),
  ('Alexa.RemoteVideoPlayer'),
  ('Alexa.SeekController'),
  ('Alexa.VideoRecorder');
