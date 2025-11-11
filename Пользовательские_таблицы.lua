local stopped = false

function OnStop()
	stopped = true
	return 50
end

function main()
	local TableOFZ = AllocTable()
	AddColumn(TableOFZ, 1, "Дата", true, QTABLE_DATE_TYPE, 13)
	AddColumn(TableOFZ, 2, "Время", true, QTABLE_TIME_TYPE, 15)
	AddColumn(TableOFZ, 3, "Код", true, QTABLE_STRING_TYPE, 15)
	AddColumn(TableOFZ, 4, "Цена", true, QTABLE_INT_TYPE, 15)
	AddColumn(TableOFZ, 5, "Успешно?", true, QTABLE_INT_TYPE, 30)

	CreateWindow(TableOFZ)
	SetWindowCaption(TableOFZ, "Таблица ОФЗ")
	SetWindowPos(TableOFZ, 0, 10, 600, 70)
	InsertRow(TableOFZ, -1)
	while stopped == false do
		local TradeDate = getInfoParam("TRADEDATE")
		local ServerTime = getInfoParam('SERVERTIME')
		local SecCode = "SU26238RMFS4"
		local LastPrice = getParamEx("TQOB", SecCode, "LAST").param_value
		local Executed = getParamEx("TQOB", SecCode, "LAST").result

		SetCell(TableOFZ, 1, 1, tostring(TradeDate))
		SetCell(TableOFZ, 1, 2, tostring(ServerTime))
		SetCell(TableOFZ, 1, 3, SecCode)
		SetCell(TableOFZ, 1, 4, tostring(LastPrice))
		SetCell(TableOFZ, 1, 5, tostring(Executed))
		sleep(100)
	end
	message("Скрипт остановлен!")
	SetCell(TableOFZ, 1, 5, "ОСТАНОВЛЕНО!")
end
