local stopped = false

function OnStop()
	stopped = true
	return 50
end

function main()
    local TableOFZ = AllocTable()
    AddColumn(TableOFZ, 1, "Легенда", true, QTABLE_STRING_TYPE, 15)
    AddColumn(TableOFZ, 2, "Год", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 3, "Месяц", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 4, "День", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 5, "Час", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 6, "Минута", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 7, "Открытие", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 8, "Максимум", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 9, "Минимум", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 10, "Закрытие", true, QTABLE_INT_TYPE, 15)
    AddColumn(TableOFZ, 11, "Объём", true, QTABLE_INT_TYPE, 15)

    CreateWindow(TableOFZ)
    SetWindowCaption(TableOFZ, "Данные с графика ОФЗ 26238 (60 мин.) - через DataSource")
    SetWindowPos(TableOFZ, 0, 10, 900, 70)

    while stopped == false do
        local OFZ_price = CreateDataSource("TQOB", "SU26238RMFS4", INTERVAL_M5)
        local OFZ_n = OFZ_price:Size()
        Clear(TableOFZ)

        for i = 1, OFZ_n, 1 do
            InsertRow(TableOFZ, -1)
            local year = OFZ_price:T(i).year
            local month = OFZ_price:T(i).month
            local day = OFZ_price:T(i).day
            local hour = OFZ_price:T(i).hour
            local minute = OFZ_price:T(i).min
            local open = OFZ_price:O(i)
            local high = OFZ_price:H(i)
            local low = OFZ_price:L(i)
            local close = OFZ_price:C(i)
            local volume = OFZ_price:V(i)
        

            SetCell(TableOFZ, i, 1, "SU26238RMFS4")
            SetCell(TableOFZ, i, 2, tostring(year))
            SetCell(TableOFZ, i, 3, tostring(month))
            SetCell(TableOFZ, i, 4, tostring(day))
            SetCell(TableOFZ, i, 5, tostring(hour))
            SetCell(TableOFZ, i, 6, tostring(minute))
            SetCell(TableOFZ, i, 7, tostring(open))
            SetCell(TableOFZ, i, 8, tostring(high))
            SetCell(TableOFZ, i, 9, tostring(low))
            SetCell(TableOFZ, i, 10, tostring(close))
            SetCell(TableOFZ, i, 11, tostring(volume))
        end
        sleep(10000)
    end
    message("Скрипт остановлен!")
end
