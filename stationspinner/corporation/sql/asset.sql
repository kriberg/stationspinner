CREATE EXTENSION IF NOT EXISTS ltree;

CREATE TABLE "corporation_asset" (
    "id" serial NOT NULL PRIMARY KEY,
    "itemID" bigint NOT NULL,
    "quantity" bigint NOT NULL,
    "locationID" bigint NOT NULL,
    "locationName" character varying(255),
    "typeID" integer NOT NULL,
    "typeName" character varying(255),
    "flag" integer NOT NULL,
    "singleton" boolean NOT NULL,
    "rawQuantity" integer,
    "path" ltree,
    "parent_id" bigint,
    "owner_id" integer NOT NULL
);
CREATE INDEX corporation_asset__path_gist_idx ON character_asset USING GIST (path);
CREATE INDEX corporation_asset_owner_id ON character_asset USING btree (owner_id);
CREATE INDEX corporation_asset_compound_owner_id_item_id ON character_asset USING btree (owner_id, "itemID");
CREATE INDEX corporation_asset_compound_owner_id_parent_id ON character_asset USING btree (owner_id, parent_id);
ALTER TABLE ONLY corporation_asset
    ADD CONSTRAINT corporation_asset_owner_id_fkey FOREIGN KEY (owner_id)
    REFERENCES corporation_corporationsheet("corporationID") DEFERRABLE INITIALLY DEFERRED;