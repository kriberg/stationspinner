CREATE EXTENSION IF NOT EXISTS ltree;

CREATE TABLE "character_asset" (
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
CREATE INDEX character_asset_path_gist_idx ON character_asset USING GIST (path);
CREATE INDEX character_asset_owner_id ON character_asset USING btree (owner_id);
ALTER TABLE ONLY character_asset
    ADD CONSTRAINT character_asset_owner_id_fkey FOREIGN KEY (owner_id)
    REFERENCES character_charactersheet("characterID") DEFERRABLE INITIALLY DEFERRED;