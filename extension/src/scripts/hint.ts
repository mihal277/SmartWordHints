interface ApiHint {
  word: string;
  start_position: number;
  end_position: number;
  definition: string;
  part_of_speech: string;
  difficulty_ranking: number;
  wordnet_sense: string;
}

export class Hint {
  word: string;

  start_position: number;

  end_position: number;

  definition: string;

  part_of_speech: string;

  difficulty_ranking: number;

  wordnet_sense: string;

  constructor(apiHint: ApiHint) {
    this.word = apiHint.word;
    this.start_position = apiHint.start_position;
    this.end_position = apiHint.end_position;
    this.definition = apiHint.definition;
    this.part_of_speech = apiHint.part_of_speech;
    this.difficulty_ranking = apiHint.difficulty_ranking;
    this.wordnet_sense = apiHint.wordnet_sense;
  }
}

export function parseApiResponse(apiResponse: any): Hint[] {
  const { hints } = apiResponse;
  return hints.map((hint: ApiHint) => new Hint(hint));
}
