function main()
    local TableOFZ = AllocTable()
    AddColumn(TableOFZ, 1, "Легенда", true, QTABLE_STRING_TYPE, 15)
    AddColumn(TableOFZ, 2, "Год", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 3, "Месяц", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 4, "День", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 5, "Час", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 6, "Открытие", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 7, "Максимум", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 8, "Минимум", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 9, "Закрытие", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 10, "Объём", true, QTABLE_INT_TYPE, 15)

    CreateWindow(TableOFZ)
    SetWindowCaption(TableOFZ, "Данные с графика ОФЗ 26238 (60 мин.)")
    SetWindowPos(TableOFZ, 0, 10, 900, 70)
    InsertRow(TableOFZ, -1)

    local OFZ_n_candles = getNumCandles("OFZPrice")
    local OFZ_price, OFZ_n, OFZ_name = getCandlesByIndex("OFZPrice", 0, 0, OFZ_n_candles)
    local year = OFZ_price[OFZ_n-1].datetime.year
    local month = OFZ_price[OFZ_n-1].datetime.month
    local day = OFZ_price[OFZ_n-1].datetime.day
    local hour = OFZ_price[OFZ_n-1].datetime.hour
    local open = OFZ_price[OFZ_n-1].open
    local high = OFZ_price[OFZ_n-1].high
    local low = OFZ_price[OFZ_n-1].low
    local close = OFZ_price[OFZ_n-1].close
    local volume = OFZ_price[OFZ_n-1].volume

    SetCell(TableOFZ, 1, 1, tostring(OFZ_name))
    SetCell(TableOFZ, 1, 2, tostring(year))
    SetCell(TableOFZ, 1, 3, tostring(month))
    SetCell(TableOFZ, 1, 4, tostring(day))
    SetCell(TableOFZ, 1, 5, tostring(hour))
    SetCell(TableOFZ, 1, 6, tostring(open-open%1))
    SetCell(TableOFZ, 1, 7, tostring(high-high%1))
    SetCell(TableOFZ, 1, 8, tostring(low-low%1))
    SetCell(TableOFZ, 1, 9, tostring(close-close%1))
    SetCell(TableOFZ, 1, 10, tostring(volume-volume%1))
end