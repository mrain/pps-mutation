/*

right now: random string + mutations, records how many times it has seen something, guesses.
only runs 1/2 experiments. really naive.

TODO:
- Implement Wrap Around
- dont guess the same thing twice
- implement context checking
( a better way to do this might be to record changes as before -> after and
keep a count of how many times we've seen a change. Everytime we see a change
record the possible contexts(sliding window) towards the end pick out common elements
in the context )

goals:
Make smarter test cases
Handle more complicated mutations
Possibly model after the scientific method ( can we model that as a search problem)
*/

package mutation.g2;

import java.util.*;
import mutation.sim.Console;
import mutation.sim.Mutagen;

public class Player extends mutation.sim.Player {
    private Random random;

    public Player() {
      Utilities.alert("Hello world");
      random = new Random();
    }

    private String randomString() {
        char[] pool = {'a', 'c', 'g', 't'};
        String result = "";
        for (int i = 0; i < 1000; ++ i)
            result += pool[Math.abs(random.nextInt() % 4)];
        return result;
    }

    public Mutagen Play(Console console, int m){
      List<Change> changes = new ArrayList<Change>();
      HashMap<String, List<Change>> actionInstances = new HashMap<>();

      HashMap<String, Integer> evidence = new HashMap<>();
	  Mutagen result = new Mutagen();
	  int experiments = 100;
	  Map<Rule, Integer> rulesWithCount = new HashMap<>();
      for (int i = 0; i < experiments; ++ i){
        result = new Mutagen();
        // run a random experiment
        String genome = randomString();
        String mutated = console.Mutate(genome);
        List<Change> changes = Utilities.diff(genome, mutated);
        System.out.println("RULES:");
		List<Rule> rules = Utilities.generateRules(changes);
		
        for(Rule r: rules) {
			//update the rulesWithCount
			if(rulesWithCount.containsKey(r)){ 
				rulesWithCount.put(r, rulesWithCount.get(r)+1);
			} else{
				rulesWithCount.put(r, 1);
			}
            System.out.println(r.formatBefore());
			System.out.println(r.after);
			
            result.add(r.formatBefore(), r.after);
        }
        boolean guess = console.Guess(result);// || result.equals(result); //how to access the actual mutagen to use .equals?
        if(guess){
            Utilities.alert("Correct!");
            break;
        }
//        // collect evidence
//        for(Change c: changes){
//          String key = c.getChange();
//          if(!evidence.containsKey(key)){
//            evidence.put(key, 0);
//          }
//          evidence.put(key, evidence.get(key)+1);
//        }

        //guess strongest evidence
//        String maxString = Utilities.argMax(evidence);
//        if(maxString != null || evidence.get(maxString) == 1){
//          Change maxEvidence = Change.fromChangeString(maxString);
//
//
//          result.add(Utilities.formatPattern(maxEvidence.before),maxEvidence.after);
//          boolean guess = console.Guess(result);
//          if(guess){
//            Utilities.alert("Correctly guessed");
//            break;
//          }
//        }
	  }
	  //////////part i added
	  Iterator hmIterator = rulesWithCount.entrySet().iterator();
	  while (hmIterator.hasNext()) { 
		Map.Entry mapElement = (Map.Entry)hmIterator.next(); 
		int marks = ((int)mapElement.getValue()); 
		System.out.println(mapElement.getKey() + " : " + marks); 
		} 
		////////////
      for(int i = 0; i < 10; ++ i){
        Mutagen result = new Mutagen();
        String genome = randomString();
        String mutated = console.Mutate(genome);
        changes.addAll(Utilities.diff(genome, mutated));
      }
      System.out.println(changes);

      for(Change c: changes){
        String after = c.after;
        if(!actionInstances.containsKey(after)){
          actionInstances.put(after, new ArrayList<Change>());
        }
        actionInstances.get(after).add(c);
      }

      List<String> uniqueActions = new ArrayList<String>(actionInstances.keySet());

      // after contexts

      for(String action: uniqueActions){
        List<Change> relatedChanges = actionInstances.get(action);
        System.out.println(action +" : "+relatedChanges.size());
        HashMap<Integer, List<String>> indexedAfterContext = new HashMap<>(); // {0:[changes at 0], 1:[changes at 1]}
        List<Integer> contextPoints = new ArrayList<Integer>(relatedChanges.get(0).afterContext.keySet());

        for(Integer index: contextPoints){
          List<String> contextsAtIndex = new ArrayList<String>();
          for(Change c: relatedChanges){
            contextsAtIndex.add(c.afterContext.get(index));
          }
          System.out.println(Utilities.collapseStrings(contextsAtIndex));
        }

      }

      return new Mutagen();
    }

}


