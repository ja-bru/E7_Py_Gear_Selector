# #### SET UP

import json

import pandas as pd

import fx_lib as fx
import paths


def main():
    with open(paths.MASTER_DATA_JSON) as json_file:
        data = json.load(json_file)

    df_items = fx.item_json_to_df(data)
    df_items = fx.gear_stats(df_items)
    df_items["error_check"] = df_items.apply(lambda row: fx.verify_item_input(row), axis=1)
    err_ids = df_items[df_items.error_check > 0]["id"].copy()
    print("Hey, we noticed some of your gear had abnormal values, so we think you should take a quick look. ")
    print("There are", err_ids.count(), "items we picked up in QA: ", err_ids.values)
    print("Note: Epic Seven does not use consistent main stat or sub stat values based on gear level, so this alert may produce false positives with event gear or lvl90 gear")

    from e7_gear.perf import log_duration
    from e7_gear.scoring import score_all_items

    with log_duration("score all gear items"):
        df_items = score_all_items(df_items)

    df_items = df_items.sort_values(by=['hero', 'Type', 'efficiency', 'enhance'])
    df_items.to_csv(paths.EQUIP_POTENTIAL_CSV)
    df_items.to_pickle(paths.EQUIP_POTENTIAL_PKL)
    export2 = df_items[['efficiency', 'hero', 'enhance', 'slot', 'level', 'set', 'rarity',
                        'mainStat', 'subStat1', 'subStat2', 'subStat3', 'subStat4', 'id', 'locked']].to_dict('records')
    with open(paths.EQUIP_POTENTIAL_JSON, 'w') as fp:
        json.dump(export2, fp)


if __name__ == "__main__":
    main()
