-- Table: public."Sensor_data"

-- DROP TABLE public."Sensor_data";

CREATE TABLE public."Sensor_data"
(
    "sensor_ID" integer NOT NULL,
    "data" integer[] NOT NULL,
    "sequence_ID" integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL DEFAULT now()
    "data_type" smallint DEFAULT 0
)