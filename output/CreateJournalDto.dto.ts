import { ApiProperty } from '@nestjs/swagger';

export class CreateJournalDto {

    @ApiProperty()
    tz_offset: number;

    @ApiProperty()
    store_id: string;

    @ApiProperty()
    je_type_id: string;

    @ApiProperty()
    journal_date: number;

    @ApiProperty()
    description: string;

    @ApiProperty({
        isArray: true,
        type: CreateTransactionDto,
    })
    transactions: CreateTransactionDto[];
}
