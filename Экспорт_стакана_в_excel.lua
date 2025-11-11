local stopped = false

function OnStop()
	stopped = true
	return 50
end

function main()
    local our_class_code = "TQOB"
    local our_sec_code = "SU26238RMFS4"
    local OFZ_stakan = getQuoteLevel2(our_class_code, our_sec_code)
    local OFZ_bid_count = OFZ_stakan.bid_count
    local OFZ_offer_count = OFZ_stakan.offer_count
    local OFZ_bids = OFZ_stakan.bid
    local OFZ_offers = OFZ_stakan.offer
    local file_name = "C:\\Robot\\Kotirovki_export_lua.txt"
    local file_writer

    while stopped == false do
        file_writer = io.open(file_name, "w")
        file_writer:write("")
        file_writer:close()
        for i = 1, OFZ_bid_count, 1 do
            file_writer = io.open(file_name, "a")
            file_writer:write(tostring(OFZ_bids[i].price))
            file_writer:close()
        end
        sleep(10000)
    end
end