public Pokemon(Dictionary<string, string> descs, string line) {
  string[] parts = line.Split('!');

  // Load basic fields
  int i = 0;
  Ability = parts[i++];
  RegionNum = parts[i++];
  Weight = parts[i++];
  Experience = parts[i++];
  Name = parts[i++];
  EggGroup = parts[i++];
  Species = parts[i++];
  Height = parts[i++];
  Type1 = parts[i++];
  Type2 = parts[i++];
  AllNum = parts[i++];

  // Load stats fields
  SpecialAttack = parts[i++];
  SpecialDefense = parts[i++];
  Hp = parts[i++];
  Attack = parts[i++];
  Defense = parts[i++];
  Speed = parts[i++];

  // Evolutions...
  int numEvolutions = int.Parse(parts[i++]);
  int evolutionLen = 3;
  int evolutionStart = i;
  // TODO STRING HERE
  Evolutions = parts[evolutionStart : evolutionStart + numEvolutions * evolutionLen];
  i += numEvolutions * evolutionLen;

  // Level moves...
  int numLevels = int.Parse(parts[i++]);
  int moveLen = 8;
  int levelStart = i;
  i += numLevels * moveLen;

  // Add all the level moves
  MoveDataContext ctxt = App.MoveContext;
  for (int move = 0; move < numLevels; move++) {
    int start = move * moveLen + levelStart;
    string moveName = Move.GetName(parts, start);
    if (!ctxt.AlreadyAddedMove(moveName)) {
      Move move = new Move(parts, start);
      move.Descr = descs[moveName];
      ctxt.AddMove(move);
    }
    App.MapContext.AddToKeyValue(Constants.KEY_POKEMON_MOVES,
                                 AllNum, moveName);
    App.MapContext.AddToKeyValue(Constants.KEY_TMS_POKEMON,
                                 moveName, AllNum);
    App.MapContext.AddToKeyValue(Constants.KEY_POKEMON_LEVELS,
                                 AllNum, parts[start + moveLen - 1]);
  }

  // TM moves...
  int numTms = int.Parse(parts[i++]);
  int tmStart = i;
  i += numTms * moveLen;

  // Add all the TM moves
  for (int move = 0; move < numTms; move++) {
    int start = move * moveLen + tmStart;
    string moveName = Move.GetName(parts, start);
    if (!ctxt.AlreadyAddedMove(moveName)) {
      Move move = new Move(parts, start);
      move.Descr = descs[moveName];
      ctxt.AddMove(move);
    }
    App.MapContext.AddToKeyValue(Constants.KEY_POKEMON_TMS,
                                 AllNum, moveName);
    App.MapContext.AddToKeyValue(Constants.KEY_TMS_POKEMON,
                                 moveName, AllNum);
  }
}

public Evolution(string[] parts, int start) {
  int i = start;
  Name = parts[i++];
  Method = parts[i++];
  Form = parts[i++];
}

public Evolution[] parseEvolutionString(string evol) {
  int evolutionLen = 3;
  string[] parts = evol.Split('!');
  Evolution[] evols = new Evolution[parts.Length / evolutionLen];
  for (int i = 0; i < evols.Length; i++) {
    evols[i] = new Evolution(parts, i * evolutionLen);
  }
  return evols;
}

public Move(string[] parts, int start) {
  int i = start;
  Accuracy = parts[i++];
  Category = parts[i++];
  Pp = parts[i++];
  Power = parts[i++];
  Name = parts[i++];
  Type = parts[i++];
  Tm = parts[i++];
}

public static string GetName(string[] parts, int start) {
  return parts[start + 4];
}
