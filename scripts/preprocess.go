package main

import (
	"compress/gzip"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"runtime"
	"runtime/pprof"
	"time"
)

var cpuprofile = flag.String("cpuprofile", "", "write cpu profile to `file`")
var memprofile = flag.String("memprofile", "", "write memory profile to `file`")

type SlayerFinal struct {
	/* final data structure for output to JSON*/
	Master_deck []string `json:"master_deck"`
	Relics      []string `json:"relics"`
}

type SlayerEvent struct {
	/* Input data structure to read form JSON*/
	Event struct {
		Gold_per_floor    []int    `json:"gold_per_floor"`
		Floor_reached     int      `json:"floor_reached"`
		Items_purged      []string `json:"items_purged"`
		Master_deck       []string `json:"master_deck"`
		Relics            []string `json:"relics"`
		Is_ascension_mode bool     `json:"is_ascension_mode"`
		Is_prod           bool     `json:"is_prod"`
		Is_daily          bool     `json:"is_daily"`
		Is_endless        bool     `json:"is_endless"`
		Victory           bool     `json:"victory"`
		Ascension_level   int      `json:"ascension_level"`
	} `json:"event"`
}

func (se SlayerEvent) BasicVictory() bool {
	/*Return true if this is a victory in the base game and not a special mode*/
	return se.Event.Victory && !se.Event.Is_prod && !se.Event.Is_daily && !se.Event.Is_endless
}

func (se SlayerEvent) MapFinal() SlayerFinal {
	/*Convert the SlayerEvent strcut to the SlayerFinal struct */
	return SlayerFinal{Master_deck: se.Event.Master_deck, Relics: se.Event.Relics}
}

func Filter(ses []SlayerEvent) []SlayerFinal {
	/*Take a sequence of SLayerEvent, filter out losing decks and map to final struct*/
	var x int = 0
	var good_results []SlayerFinal

	for _, s := range ses {
		if s.BasicVictory() {
			x += 1
			good_results = append(good_results, s.MapFinal())
		}
	}
	//fmt.Println(len(good_results))
	//fmt.Println(len(ses))

	return good_results
}

func main() {
	flag.Parse()
	if *cpuprofile != "" {
		f, err := os.Create(*cpuprofile)
		if err != nil {
			log.Fatal("could not create CPU profile: ", err)
		}
		defer f.Close() // error handling omitted for example
		if err := pprof.StartCPUProfile(f); err != nil {
			log.Fatal("could not start CPU profile: ", err)
		}
		defer pprof.StopCPUProfile()
	}

	start := time.Now()
	// get all json files that need to be loaded and parsed
	data_dir := "data/full/Monthly_2020_11"
	files, err := os.ReadDir(data_dir)
	if err != nil {
		log.Fatal(err)
	}
	//fmt.Println(len(files))

	var good_results []SlayerFinal
	var start_count, final_count int

	for idx := 0; idx < 100; idx++ {
		f := files[idx]
		// Open our jsonFile
		jsonFileGZ, err := os.Open(data_dir + "/" + f.Name())
		// if we os.Open returns an error then handle it
		if err != nil {
			fmt.Println(err)
		}
		//fmt.Println("Successfully Opened data")

		// load the JSON, un-compress and unmarshall
		var results []SlayerEvent
		jsonFile, err := gzip.NewReader(jsonFileGZ)
		if err != nil {
			log.Fatal(err)
		}
		byte_value, _ := ioutil.ReadAll(jsonFile)

		json.Unmarshal([]byte(byte_value), &results)
		jsonFile.Close()

		// filter results to a single
		filtered := Filter(results)
		for _, filt := range filtered {
			good_results = append(good_results, filt)
		}

		// keep track of size of things
		start_count += len(results)
		final_count += len(filtered)
		if idx%10 == 0 {
			//fmt.Println(float32(final_count) / float32(start_count))
		}
	}

	good_bytes, err := json.MarshalIndent(good_results, "", "    ")
	os.WriteFile("data/victory.json", good_bytes, 0700)

	end := time.Now()

	elapsed := end.Sub(start)
	fmt.Println(final_count)
	fmt.Println(start_count)
	fmt.Println(elapsed)

	if *memprofile != "" {
		f, err := os.Create(*memprofile)
		if err != nil {
			log.Fatal("could not create memory profile: ", err)
		}
		defer f.Close() // error handling omitted for example
		runtime.GC()    // get up-to-date statistics
		if err := pprof.WriteHeapProfile(f); err != nil {
			log.Fatal("could not write memory profile: ", err)
		}
	}

}
