CREATE TABLE marketdata
(
    typeid          integer NOT NULL,
    locationid      integer NOT NULL,
    buy_volume      numeric(20,2),
    buy_avg         numeric(20,2),
    buy_max         numeric(20,2),
    buy_min         numeric(20,2),
    buy_stddev      numeric(20,2),
    buy_median      numeric(20,2),
    buy_percentile  numeric(20,2),
    sell_volume     numeric(20,2),
    sell_avg        numeric(20,2),
    sell_max        numeric(20,2),
    sell_min        numeric(20,2),
    sell_stddev     numeric(20,2),
    sell_median     numeric(20,2),
    sell_percentile numeric(20,2),
    timestamp       timestamp with time zone  not null,
    PRIMARY KEY (typeid, locationid),
    CONSTRAINT invtypes_typeid_fkey FOREIGN KEY (typeid)
        REFERENCES invtypes (typeid) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT mapdenormalize_itemid FOREIGN KEY (locationid)
        REFERENCES mapdenormalize (itemid) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

