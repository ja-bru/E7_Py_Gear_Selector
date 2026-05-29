
import pandas as pd

import paths


def main():
    df_items = pd.read_pickle(paths.EQUIP_POTENTIAL_PKL)

    x1 = df_items['efficiency'].quantile(q=0.4)
    x2 = df_items['max_eff'].quantile(q=0.3)
    x3 = df_items['rating'].quantile(q=0.4)
    x4 = df_items['current_eff'].quantile(q=0.3)

    print("number of items", len(df_items))
    print("number of unequipped items", len(df_items[df_items.hero == '']))

    low_items = df_items[
        (df_items.efficiency <= x1) & (df_items.max_eff <= x2)
        & (df_items.rating <= x3) & (df_items.current_eff <= x4) & (df_items.SPD <= 8)
    ].copy()

    print("number of items to delete", len(low_items))
    print("number of unequipped items to delete", len(low_items[low_items.hero == '']))

    low_items[low_items.hero == ''].id.to_csv(paths.REMOVE_LIST_CSV)


if __name__ == "__main__":
    main()
