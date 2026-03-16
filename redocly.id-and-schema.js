module.exports = function idAndSchemaPlugin() {
  return {
    id: 'extend-id-and-schema',
    typeExtension: {
      oas3(types) {
        return {
          ...types,
          Schema: {
            ...types.Schema,
            properties: {
              ...types.Schema.properties,
              $id: { type: 'string' },
              $schema: { type: 'string' },
              definitions: {
                type: 'object',
                additionalProperties: { $ref: '#/types/Schema' },
              },
            },
          },
        };
      },
    },
  };
};
