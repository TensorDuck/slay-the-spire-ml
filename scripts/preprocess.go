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
	"sync"
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

func loadJson(fileName string, fileNumber int, rawCount *int, wg *sync.WaitGroup, saveResults *[][]SlayerFinal) {
	defer wg.Done()

	jsonFileGZ, err := os.Open(fileName)
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

	// filter results by victory condition and save
	(*saveResults)[fileNumber] = Filter(results)
	(*rawCount) += len(results)
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

	// initialize variables
	start := time.Now()
	var startCount, finalCount int
	var wg sync.WaitGroup

	// get all json files that need to be loaded and parsed
	data_dir := "data/full/Monthly_2020_11"
	files, err := os.ReadDir(data_dir)
	if err != nil {
		log.Fatal(err)
	}
	//fmt.Println(len(files))

	//nFiles := len(files)
	nFiles := 100
	good_results := make([][]SlayerFinal, nFiles)

	// Open all jsonFiles with concurrency
	for idx := 0; idx < nFiles; idx++ {
		wg.Add(1)
		go loadJson(data_dir+"/"+files[idx].Name(), idx, &startCount, &wg, &good_results)
	}
	wg.Wait()

	// Flatten all collected JSON files
	// count how many JSON elements to save
	for idx := 0; idx < len(good_results); idx++ {
		finalCount += len(good_results[idx])
	}
	finalResults := make([]SlayerFinal, finalCount)
	// now add all the  good results to the final results
	finalIdx := 0
	for idx := 0; idx < len(good_results); idx++ {
		for _, val := range good_results[idx] {
			finalResults[finalIdx] = val
			finalIdx += 1
		}
	}

	good_bytes, err := json.MarshalIndent(good_results, "", "    ")
	os.WriteFile("data/victory.json", good_bytes, 0700)

	end := time.Now()

	elapsed := end.Sub(start)
	fmt.Println(startCount)
	fmt.Println(finalCount)
	fmt.Println(float32(finalCount) / float32(startCount))
	fmt.Println(elapsed)

	// save memory profile file
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
