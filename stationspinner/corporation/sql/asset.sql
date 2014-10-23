CREATE EXTENSION IF NOT EXISTS ltree;

CREATE TABLE "corporation_asset" (
    "id" serial NOT NULL PRIMARY KEY,
    "itemID" bigint NOT NULL,
    "quantity" bigint NOT NULL,
    "locationID" bigint NOT NULL,
    "typeID" integer NOT NULL,
    "flag" integer NOT NULL,
    "singleton" boolean NOT NULL,
    "rawQuantity" integer,
    "path" ltree,
    "owner_id" integer NOT NULL
);
CREATE INDEX corporation_asset_path_gist_idx ON corporation_asset USING GIST (path);
CREATE INDEX corporation_asset_owner_id ON corporation_asset USING btree (owner_id);
ALTER TABLE ONLY corporation_asset
    ADD CONSTRAINT corporation_asset_owner_id_fkey FOREIGN KEY (owner_id)
    REFERENCES corporation_corporationsheet("corporationID") DEFERRABLE INITIALLY DEFERRED;